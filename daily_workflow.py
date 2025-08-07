#!/usr/bin/env python3
"""
Workflow quotidien automatisé pour la génération de contenu MTC.

Ce script gère le processus complet de traitement de contenu :
1. Vérification des nouveaux PDF à traiter
2. Exécution du workflow de traitement
3. Génération de contenu basé sur la base de connaissances
4. Validation et préparation pour publication
5. Génération du rapport quotidien
"""
import os
import asyncio
import json
import aiofiles
import logging
from dataclasses import asdict, is_dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Any

from dotenv import load_dotenv

# Configuration du logging
log_file = "daily_workflow.log"
try:
    # Essayer de supprimer le fichier de log s'il existe
    if os.path.exists(log_file):
        try:
            os.remove(log_file)
        except PermissionError:
            # Si le fichier est verrouillé, ajouter un horodatage au nom du fichier
            import time
            log_file = f"daily_workflow_{int(time.time())}.log"
            
    # Configurer le logging avec le nouveau nom de fichier
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
except Exception as e:
    # En cas d'erreur, utiliser uniquement la console
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )
    logging.error(f"Impossible de configurer le fichier de log: {e}. Utilisation de la console uniquement.")
logger = logging.getLogger(__name__)

# Chargement des variables d'environnement
load_dotenv()

# Configuration des chemins
BASE_DIR = Path(__file__).resolve().parent
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"
REPORTS_DIR = OUTPUT_DIR / "reports"
CONTENT_DIR = OUTPUT_DIR / "content"

# Création des dossiers nécessaires
for directory in [INPUT_DIR, OUTPUT_DIR, REPORTS_DIR, CONTENT_DIR]:
    directory.mkdir(exist_ok=True, parents=True)


class CustomEncoder(json.JSONEncoder):
    """Encodeur JSON personnalisé pour gérer les dataclasses, enums et Path."""
    def default(self, o: Any) -> Any:
        if is_dataclass(o):
            return asdict(o)
        if isinstance(o, Enum):
            return o.value
        if isinstance(o, Path):
            return str(o)
        return super().default(o)


class DailyWorkflow:
    """Classe principale pour gérer le workflow quotidien."""

    def __init__(self):
        """Initialise le contexte et les agents."""
        self.context = {
            "date_execution": datetime.now().strftime("%Y-%m-%d"),
            "statistiques": {
                "pdf_traites": 0,
                "txt_traites": 0,
                "articles_generes": 0,
                "publications_sociales": 0,
                "visuels_crees": 0,
                "erreurs": [],
            },
            "contenus_generes": {
                "articles": [],
                "publications": [],
                "visuels": [],
                "fichiers": [],
            }
        }
        self.agents = {}
        logger.info("Workflow initialisé.")

    async def initialize_agents(self):
        """Initialise tous les agents nécessaires de manière asynchrone."""
        logger.info("Initialisation des agents...")
        from agents.pdf_analyzer import PDFAnalyzerAgent
        from agents.theme_manager import ThemeManagerAgent
        from agents.content_strategy import ContentStrategyAgent
        from agents.blog_writer import BlogWriterAgent
        from agents.social_creator import SocialCreatorAgent
        from agents.visual_creator import VisualCreatorAgent
        from agents.validator import ValidatorAgent

        self.agents = {
            'pdf_analyzer': PDFAnalyzerAgent(),
            'theme_manager': ThemeManagerAgent(),
            'content_strategy': ContentStrategyAgent(),
            'blog_writer': BlogWriterAgent(),
            'social_creator': SocialCreatorAgent(),
            'visual_creator': VisualCreatorAgent(),
            'validator': ValidatorAgent()
        }
        logger.info("Tous les agents ont été initialisés.")

    async def check_for_new_files(self) -> List[Path]:
        """Vérifie la présence de nouveaux fichiers PDF ou TXT à traiter."""
        logger.info(f"Recherche de nouveaux fichiers dans : {INPUT_DIR}")
        pdf_files = list(INPUT_DIR.glob("*.pdf"))
        txt_files = list(INPUT_DIR.glob("*.txt"))
        all_files = pdf_files + txt_files
        if not all_files:
            logger.info("Aucun nouveau fichier (PDF/TXT) détecté.")
        else:
            logger.info(f"{len(all_files)} nouveau(x) fichier(s) détecté(s): {', '.join(f.name for f in all_files)}")
        return all_files

    async def process_file(self, file_path: Path) -> Dict:
        """Traite un seul fichier (PDF ou TXT) via le pipeline d'agents."""
        logger.info(f"--- Début du traitement du fichier : {file_path.name} ---")
        try:
            # 1. Analyse du fichier
            if file_path.suffix.lower() == '.pdf':
                analysis_result = await self.agents['pdf_analyzer'].analyze_pdf(str(file_path))
                content = analysis_result.get('resume', '')
                self.context['statistiques']['pdf_traites'] += 1
            elif file_path.suffix.lower() == '.txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                analysis_result = {'resume': content, 'metadata': {'source': file_path.name}}
                self.context['statistiques']['txt_traites'] += 1
            else:
                raise ValueError(f"Format de fichier non supporté : {file_path.suffix}")

            # 2. Analyse thématique
            theme_analysis = await self.agents['theme_manager'].analyze_content(content=content, content_type="pdf_analysis")

            # 3. Stratégie de contenu
            content_strategy = await self.agents['content_strategy'].generate_strategy(analysis=analysis_result, theme_analysis=theme_analysis)

            # 4. Rédaction de l'article de blog
            topic = content_strategy.get('suggested_topics', ['Médecine Traditionnelle Chinoise'])[0]
            blog_post_dict = await self.agents['blog_writer'].write_article(topic=topic, target_audience="grand public", style="professionnel")
            
            # Vérifier si la génération a réussi
            if blog_post_dict.get('status') == 'success':
                # Extraire le contenu de l'article et les métadonnées
                article_content = blog_post_dict.get('article', '')
                metadata = blog_post_dict.get('metadata', {})
                
                # Créer un dictionnaire avec le contenu et les métadonnées
                blog_post = {
                    'content': article_content,
                    'metadata': metadata
                }
                
                self.context['contenus_generes']['articles'].append(blog_post)
                self.context['statistiques']['articles_generes'] += 1
            else:
                error_msg = blog_post_dict.get('message', 'Erreur inconnue lors de la génération de l\'article')
                logger.error(f"Échec de la génération de l'article: {error_msg}")
                blog_post_dict = {'error': error_msg}

            # 5. Validation du contenu
            validation_result = await self.agents['validator'].validate_content(content=blog_post_dict, content_type="article_blog")

            # 6. Création des publications pour les réseaux sociaux
            social_posts = await self.agents['social_creator'].create_posts(content_data=blog_post_dict)
            self.context['contenus_generes']['publications'].extend(social_posts)
            self.context['statistiques']['publications_sociales'] += len(social_posts)

            # 7. Création des visuels
            visual_elements = []
            for post in social_posts:
                prompt_input = {
                    'type_visuel': post.get('type_visuel', 'citation'),
                    'theme': post.get('theme', 'MTC'),
                    'elements': [post.get('content', '')],
                    'style': 'moderne'
                }
                visual = self.agents['visual_creator'].generate_prompt(prompt_input)
                visual_elements.append(visual)
            self.context['contenus_generes']['visuels'].extend(visual_elements)
            self.context['statistiques']['visuels_crees'] += len(visual_elements)

            # 8. Assemblage des résultats
            result = {
                'source_file': file_path.name,
                'analysis': analysis_result,
                'theme_analysis': theme_analysis,
                'content_strategy': content_strategy,
                'blog_post': blog_post_dict.get('article', '') if isinstance(blog_post_dict, dict) else str(blog_post_dict),
                'blog_metadata': blog_post_dict.get('metadata', {}) if isinstance(blog_post_dict, dict) else {},
                'validation': validation_result,
                'social_posts': social_posts,
                'visual_elements': visual_elements,
            }

            # 9. Sauvegarde des résultats
            await self.save_results(result, file_path.stem)
            logger.info(f"--- Fin du traitement du fichier : {file_path.name} ---")
            return result

        except Exception as e:
            logger.error(f"Erreur lors du traitement du fichier {file_path.name}: {e}", exc_info=True)
            self.context['statistiques']['erreurs'].append({'fichier': file_path.name, 'erreur': str(e)})
            return {}

    async def save_results(self, result: Dict, base_filename: str):
        """Sauvegarde les résultats du traitement dans des fichiers JSON et Markdown."""
        output_dir = CONTENT_DIR / base_filename
        output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Sauvegarde des résultats dans : {output_dir}")

        try:
            # Sauvegarde du résultat complet
            result_file = output_dir / 'resultat_complet.json'
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2, cls=CustomEncoder)

            # Sauvegarde de l'article de blog
            blog_post = result.get('blog_post')
            if blog_post:
                blog_file = output_dir / 'article_blog.md'
                content = blog_post.get('content', '') if isinstance(blog_post, dict) else str(blog_post)
                with open(blog_file, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            logger.info(f"Résultats pour '{base_filename}' sauvegardés avec succès.")

        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des fichiers pour {base_filename}: {e}", exc_info=True)
            # Ne propagez pas l'erreur pour ne pas bloquer le reste du workflow
            self.context['statistiques']['erreurs'].append({'fichier': base_filename, 'erreur': f"Sauvegarde échouée: {e}"})


    async def generate_daily_report(self):
        """Génère le rapport quotidien de production en JSON et Markdown."""
        logger.info("Génération du rapport quotidien...")
        try:
            report_data = {
                'date': self.context['date_execution'],
                'statistiques': self.context['statistiques'],
                'resume_contenu': {
                    'articles': [
                        {'titre': a.get('metadata', {}).get('title', 'Titre inconnu'), 'mots': len(a.get('content', '').split())}
                        for a in self.context['contenus_generes']['articles'] if isinstance(a, dict)
                    ],
                    'publications': len(self.context['contenus_generes']['publications']),
                    'visuels': len(self.context['contenus_generes']['visuels'])
                },
                'erreurs': self.context['statistiques']['erreurs']
            }

            # Sauvegarde du rapport JSON
            report_file_json = REPORTS_DIR / f"rapport_{self.context['date_execution']}.json"
            with open(report_file_json, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2, cls=CustomEncoder)

            # Génération et sauvegarde du rapport Markdown
            report_file_md = REPORTS_DIR / f"rapport_{self.context['date_execution']}.md"
            await self._generate_human_readable_report(report_data, report_file_md)

            logger.info(f"Rapport quotidien généré : {report_file_json.name} et {report_file_md.name}")
            return report_data
        except Exception as e:
            logger.error(f"Erreur lors de la génération du rapport : {e}", exc_info=True)
            return {}

    async def _generate_human_readable_report(self, report_data: Dict, output_path: Path):
        """Génère une version lisible du rapport en Markdown."""
        stats = report_data['statistiques']
        contenus = report_data['resume_contenu']
        
        lines = [
            f"# RAPPORT QUOTIDIEN - {report_data['date']}",
            "## 📊 Statistiques de production",
            f"- 📄 Fichiers traités: {stats.get('pdf_traites', 0) + stats.get('txt_traites', 0)}",
            f"- 📝 Articles générés: {stats.get('articles_generes', 0)}",
            f"- 📱 Publications sociales: {stats.get('publications_sociales', 0)}",
            f"- 🎨 Visuels créés: {stats.get('visuels_crees', 0)}",
            f"- ❌ Erreurs: {len(stats.get('erreurs', []))}",
            "\n## 📝 Contenus générés",
            "### Articles de blog"
        ]
        
        articles = contenus.get('articles', [])
        if articles:
            for article in articles:
                lines.append(f"- {article.get('titre', 'Sans titre')} ({article.get('mots', 0)} mots)")
        else:
            lines.append("- Aucun article généré.")

        if stats.get('erreurs'):
            lines.append("\n## ❌ Erreurs rencontrées")
            for error in stats['erreurs']:
                lines.append(f"- **Fichier/Étape:** {error.get('fichier', 'N/A')} - **Erreur:** {error.get('erreur', 'Inconnue')}")
        
        # Utilise aiofiles pour l'écriture asynchrone
        async with aiofiles.open(output_path, 'w', encoding='utf-8') as f:
            await f.write("\n".join(lines))
    
    async def run(self, max_concurrent_tasks: int = 3):
        """
        Exécute le workflow quotidien complet.
        
        Args:
            max_concurrent_tasks: Nombre maximum de tâches à exécuter en parallèle
        """
        logger.info("=== DÉMARRAGE DU WORKFLOW QUOTIDIEN ===")
        start_time = datetime.now()
        
        try:
            # Initialisation des agents
            await self.initialize_agents()
            
            # Vérification des nouveaux fichiers (PDF ou TXT)
            input_files = await self.check_for_new_files()
            
            if input_files:
                logger.info(f"Traitement de {len(input_files)} fichiers en parallèle (max {max_concurrent_tasks} tâches simultanées)")
                
                # Création d'une sémaphore pour limiter le nombre de tâches concurrentes
                semaphore = asyncio.Semaphore(max_concurrent_tasks)
                
                async def process_with_semaphore(file_path):
                    async with semaphore:
                        try:
                            return await self.process_file(file_path)
                        except Exception as e:
                            logger.error(f"Erreur lors du traitement de {file_path.name}: {str(e)}", exc_info=True)
                            return {"status": "error", "file": str(file_path), "error": str(e)}
                
                # Création des tâches de traitement
                tasks = [process_with_semaphore(file_path) for file_path in input_files]
                
                # Exécution des tâches en parallèle avec gestion des erreurs
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Traitement des résultats
                for result in results:
                    if isinstance(result, Exception):
                        logger.error(f"Erreur dans une tâche de traitement: {str(result)}")
                    elif isinstance(result, dict) and result.get('status') == 'error':
                        logger.error(f"Erreur de traitement: {result.get('error')}")
            else:
                logger.info("Aucun fichier à traiter, génération de contenu à partir de la base de connaissances")
                await self.generate_content_from_knowledge()
            
            # Génération du rapport quotidien
            await self.generate_daily_report()
            
            # Calcul du temps d'exécution
            duration = (datetime.now() - start_time).total_seconds() / 60
            logger.info(f"=== WORKFLOW TERMINÉ EN {duration:.1f} MINUTES ===")
            
            return True
            
        except Exception as e:
            logger.error(f"ERREUR LORS DE L'EXÉCUTION DU WORKFLOW: {str(e)}", exc_info=True)
            return False


async def main():
    """Fonction principale."""
    workflow = DailyWorkflow()
    success = await workflow.run()
    return 0 if success else 1


if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))
