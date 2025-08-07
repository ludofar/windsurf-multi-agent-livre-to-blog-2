#!/usr/bin/env python3
"""
Point d'entrée principal du système multi-agent pour l'analyse de livres MTC.
"""
import os
import asyncio
import argparse
from pathlib import Path
from dotenv import load_dotenv
from agents.pdf_analyzer import PDFAnalyzerAgent
from agents.content_strategy import ContentStrategyAgent
from agents.blog_writer import BlogWriterAgent
from agents.social_creator import SocialCreatorAgent
from agents.visual_creator import VisualCreatorAgent
from agents.theme_manager import ThemeManagerAgent
from agents.validator import ValidatorAgent

# Chargement des variables d'environnement
load_dotenv()

# Configuration des chemins
BASE_DIR = Path(__file__).parent
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"

# Création des dossiers nécessaires
for directory in [INPUT_DIR, OUTPUT_DIR]:
    directory.mkdir(exist_ok=True, parents=True)

class MTCAnalysisOrchestrator:
    """Orchestrateur principal pour le système multi-agent MTC."""
    
    def __init__(self):
        # Initialisation des agents
        self.agents = {
            'pdf_analyzer': PDFAnalyzerAgent(),
            'theme_manager': ThemeManagerAgent(),
            'content_strategy': ContentStrategyAgent(),
            'blog_writer': BlogWriterAgent(),
            'visual_creator': VisualCreatorAgent(),
            'social_creator': SocialCreatorAgent(),
            'validator': ValidatorAgent()
        }
        self.context = {}
    
    async def run_analysis(self, pdf_path: str):
        """Exécute le pipeline d'analyse complet."""
        try:
            # 1. Analyse du PDF
            print("🚀 Démarrage de l'analyse du PDF...")
            self.context['pdf_path'] = pdf_path
            pdf_analysis = await self.agents['pdf_analyzer'].process(self.context)
            self.context.update(pdf_analysis)
            
            # 2. Gestion des thèmes et cohérence
            print("🎨 Analyse de la cohérence thématique...")
            theme_analysis = await self.agents['theme_manager'].process(self.context)
            self.context.update(theme_analysis)
            
            # 3. Stratégie de contenu
            print("📝 Élaboration de la stratégie de contenu...")
            content_strategy = await self.agents['content_strategy'].process(self.context)
            self.context.update(content_strategy)
            
            # 4. Rédaction des articles de blog
            print("✍️  Rédaction des articles de blog...")
            blog_content = await self.agents['blog_writer'].process(self.context)
            self.context.update(blog_content)
            
            # 5. Création des visuels
            print("🎨 Génération des visuels...")
            visual_content = await self.agents['visual_creator'].process(self.context)
            self.context.update(visual_content)
            
            # 6. Création du contenu pour les réseaux sociaux
            print("📱 Préparation des publications sociales...")
            social_content = await self.agents['social_creator'].process(self.context)
            self.context.update(social_content)
            
            # 7. Validation finale
            print("🔍 Validation du contenu...")
            validation = await self.agents['validator'].process(self.context)
            self.context.update(validation)
            
            print("✅ Analyse terminée avec succès !")
            return self.context
            
        except Exception as e:
            print(f"❌ Erreur lors de l'analyse: {str(e)}")
            raise

def main():
    # Configuration des arguments en ligne de commande
    parser = argparse.ArgumentParser(description="Système d'analyse de livres MTC")
    parser.add_argument(
        '--input', 
        type=str, 
        required=True,
        help="Chemin vers le fichier PDF à analyser"
    )
    parser.add_argument(
        '--output', 
        type=str, 
        default=str(OUTPUT_DIR),
        help="Dossier de sortie pour les résultats"
    )
    
    args = parser.parse_args()
    
    # Vérification du fichier d'entrée
    if not os.path.isfile(args.input):
        print(f"Erreur: Le fichier {args.input} n'existe pas.")
        return
    
    # Création de l'orchestrateur et exécution
    orchestrator = MTCAnalysisOrchestrator()
    
    try:
        # Exécution asynchrone
        asyncio.run(orchestrator.run_analysis(args.input))
    except KeyboardInterrupt:
        print("\nOpération annulée par l'utilisateur.")
    except Exception as e:
        print(f"Une erreur est survenue: {str(e)}")

if __name__ == "__main__":
    main()
