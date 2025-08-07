from .base_agent import BaseAgent
from typing import Dict, Any, List, Optional
import json
import logging
import os
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)

class ToneType(str, Enum):
    INFORMATIF = "informatif"
    ÉDUCATIF = "éducatif"
    CONVERSATIONNEL = "conversationnel"
    INSPIRANT = "inspirant"

class AudienceLevel(str, Enum):
    DÉBUTANT = "débutant"
    INTERMÉDIAIRE = "intermédiaire"
    AVANCÉ = "avancé"
    EXPERT = "expert"

@dataclass
class SEOData:
    meta_title: str
    meta_description: str
    focus_keyword: str
    secondary_keywords: List[str] = field(default_factory=list)
    slug: Optional[str] = None

@dataclass
class BlogPost:
    title: str
    content: str
    seo: SEOData
    word_count: int
    reading_time: int  # in minutes
    last_updated: str
    categories: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)

class BlogWriterAgent(BaseAgent):
    """
    Agent spécialisé dans la rédaction d'articles de blog sur la Médecine Traditionnelle Chinoise.
    Crée des contenus optimisés SEO de 1500 à 2000 mots, adaptés à différents niveaux de compréhension.
    """
    
    def __init__(self, model: str = None):
        default_model = os.getenv('DEFAULT_MODEL', 'qwen/qwen3-coder')
        super().__init__(
            name="Blog Writer Agent",
            model=model or default_model
        )
        
        # Paramètres par défaut
        self.default_word_count = 1750  # Cible moyenne
        self.words_per_minute = 200  # Vitesse de lecture moyenne
    
    def generate_prompt(self, input_data: Dict[str, Any]) -> str:
        """
        Génère un prompt détaillé pour la rédaction d'un article de blog sur la MTC.
        
        Args:
            input_data: Doit contenir 'theme', 'mots_cles', 'ton', 'audience', 'strategie'
            
        Returns:
            str: Prompt structuré pour la génération d'article
        """
        theme = input_data.get('theme', 'Médecine Traditionnelle Chinoise')
        mots_cles = input_data.get('mots_cles', ['MTC', 'santé naturelle'])
        ton = input_data.get('ton', ToneType.INFORMATIF)
        audience = input_data.get('audience', AudienceLevel.DÉBUTANT)
        strategie = input_data.get('strategie', {})
        
        # Récupération des éléments de stratégie
        angle = strategie.get('angle', '')
        objectif = strategie.get('objectif', 'informer')
        
        return f"""
        # INSTRUCTIONS POUR LA RÉDACTION D'ARTICLE BLOG MTC
        
        ## CONTEXTE
        Tu es un expert en Médecine Traditionnelle Chinoise avec une excellente maîtrise de la rédaction web SEO.
        
        ## MISSION
        Rédiger un article de blog complet sur le thème : "{theme}"
        
        ## SPÉCIFICATIONS TECHNIQUES
        - Longueur : Entre 1500 et 2000 mots (cible : {self.default_word_count} mots)
        - Style : {ton}
        - Niveau du public : {audience}
        - Angle d'approche : {angle}
        - Objectif principal : {objectif}
        
        ## STRUCTURE OBLIGATOIRE
        
        ```markdown
        ---
        title: "[Titre accrocheur et optimisé SEO]"
        description: "[Meta description de 150-160 caractères avec mot-clé principal]"
        date: "{datetime.now().strftime('%Y-%m-%d')}"
        categories: ["Médecine Traditionnelle Chinoise"]
        tags: {json.dumps(mots_cles)}
        keywords: "{', '.join(mots_cles)}"
        reading_time: X min
        ---
        
        # [Titre principal - H1]
        
        ## Introduction
        [150-200 mots]
        - Accroche percutante
        - Présentation du sujet et de son importance en MTC
        - Annonce du plan de l'article
        
        ## [Section 1 - H2]
        [300-400 mots]
        - Sous-section 1.1 (H3)
        - Sous-section 1.2 (H3)
        
        ## [Section 2 - H2]
        [300-400 mots]
        - Sous-section 2.1 (H3)
        - Sous-section 2.2 (H3)
        
        ## [Section 3 - H2]
        [300-400 mots]
        - Sous-section 3.1 (H3)
        - Sous-section 3.2 (H3)
        
        ## Conclusion
        [150-200 mots]
        - Résumé des points clés
        - Appel à l'action clair
        - Lien vers des ressources complémentaires
        
        ## FAQ (Optionnel)
        - Question 1 ?
          Réponse concise.
        - Question 2 ?
          Réponse concise.
        ```
        
        ## CONSIGNES DE RÉDACTION
        
        1. **TITRE ET MÉTA-DONNÉES**
           - Créer un titre principal accrocheur (H1) de 50-60 caractères
           - Rédiger une méta-description de 150-160 caractères avec le mot-clé principal
           - Utiliser des mots-clés stratégiquement dans les titres et sous-titres
           
        2. **STYLE ET TON**
           - Adapter le niveau de langage au public cible ({audience})
           - Utiliser un ton {ton}
           - Expliquer les termes techniques de MTC
           - Varier la longueur des phrases pour le rythme
           
        3. **OPTIMISATION SEO**
           - Utiliser les mots-clés principaux : {', '.join(mots_cles[:3])}
           - Intégrer des variantes sémantiques
           - Optimiser les balises alt des images
           - Créer des liens internes vers d'autres articles
           
        4. **MISE EN FORME**
           - Paragraphes courts (3-4 lignes maximum)
           - Listes à puces pour les énumérations
           - Mots en gras pour les concepts importants
           - Citations mises en valeur
           
        5. **ÉLÉMENTS D'ENGAGEMENT**
           - Questions rhétoriques
           - Exemples concrets
           - Anecdotes pertinentes
           - Appels à l'action clairs
        
        ## EXIGENCES TECHNIQUES
        - Format : Markdown pur
        - Encodage : UTF-8
        - Pas de HTML dans le contenu
        - Utiliser la syntaxe Markdown pour les liens : [texte](URL)
        - Pour les images : ![alt text](image.jpg "Titre optionnel")
        
        ## EXEMPLE DE STRUCTURE DE RÉPONSE
        
        ```markdown
        ---
        title: "[Titre optimisé SEO]"
        description: "[Description concise avec mot-clé]"
        date: "2023-11-15"
        categories: ["Médecine Traditionnelle Chinoise"]
        tags: ["acupuncture", "santé naturelle", "MTC"]
        keywords: "acupuncture, points méridiens, médecine chinoise"
        reading_time: 9 min
        ---
        
        # [Titre principal accrocheur]
        
        ## Introduction
        [Contenu de l'introduction...]
        
        ## [Première section thématique]
        [Contenu...]
        
        ### [Sous-section]
        [Détails...]
        
        ## Conclusion
        [Résumé et appel à l'action...]
        ```
        
        Commence directement par le format Markdown, sans commentaires supplémentaires.
        """
    
    def parse_response(self, response: str) -> Dict[str, Any]:
        """Traite la réponse Markdown du modèle."""
        return {"content": response}

    def _parse_response(self, response: str) -> Dict[str, Any]:
        """
        Parse la réponse du modèle qui peut être soit du JSON, soit du Markdown brut.
        
        Args:
            response: Réponse brute du modèle (JSON ou Markdown)
            
        Returns:
            Dict contenant le contenu et les métadonnées de l'article
        """
        # Essayer d'abord de parser en tant que JSON
        trimmed_response = response.strip()
        if (trimmed_response.startswith('{') and trimmed_response.endswith('}')) or \
           (trimmed_response.startswith('[') and trimmed_response.endswith(']')):
            try:
                return json.loads(trimmed_response)
            except json.JSONDecodeError:
                # Si le parsing JSON échoue, continuer avec le traitement Markdown
                pass
        
        # Si ce n'est pas du JSON valide, traiter comme du Markdown
        return {
            'content': response,
            'status': 'success',
            'metadata': {
                'title': 'Article de blog généré',
                'word_count': len(response.split()),
                'format': 'markdown'
            }
        }
    
    def _estimate_reading_time(self, word_count: int) -> str:
        """Estime le temps de lecture en fonction du nombre de mots"""
        words_per_minute = 200  # Vitesse moyenne de lecture
        minutes = round(word_count / words_per_minute)
        return f"{minutes} min de lecture"
        
    async def write_article(self, topic: str, target_audience: str = "débutant", 
                          style: str = "informatif", word_count: int = 1750) -> Dict[str, Any]:
        """
        Rédige un article de blog complet sur un sujet donné.
        
        Args:
            topic: Sujet de l'article
            target_audience: Niveau du public cible (débutant, intermédiaire, avancé, expert)
            style: Style d'écriture (informatif, éducatif, conversationnel, inspirant)
            word_count: Nombre de mots cible pour l'article
            
        Returns:
            Dict contenant l'article et ses métadonnées
        """
        try:
            # Préparation des données pour le prompt
            input_data = {
                'theme': topic,
                'mots_cles': [topic],
                'ton': style,
                'audience': target_audience,
                'strategie': {
                    'angle': f"Approche {style} sur {topic} en MTC",
                    'objectif': 'informer' if style == 'informatif' else 'éduquer'
                }
            }
            
            # Génération du prompt
            prompt = self.generate_prompt(input_data)
            
            # Appel au modèle
            response = await self.process({'content': prompt})
            
            # Traitement de la réponse
            if not isinstance(response, dict):
                response = {'content': str(response)}
            
            # Si la réponse contient une erreur, la retourner telle quelle
            if response.get('status') == 'error' or 'error' in response:
                return response
                
            # Extraire le contenu de l'article
            article_content = response.get('content', '')
            
            # Création des métadonnées SEO
            seo_data = SEOData(
                meta_title=response.get('metadata', {}).get('title', f"{topic} - Guide Complet en MTC"),
                meta_description=response.get('metadata', {}).get('description', 
                    f"Découvrez tout sur {topic} en Médecine Traditionnelle Chinoise. Conseils pratiques et explications détaillées."),
                focus_keyword=response.get('metadata', {}).get('focus_keyword', topic),
                secondary_keywords=response.get('metadata', {}).get('secondary_keywords', 
                    [f"{topic} MTC", f"médecine chinoise {topic}"])
            )
            
            # Création de l'objet BlogPost
            word_count = len(article_content.split())
            blog_post = BlogPost(
                title=response.get('metadata', {}).get('title', f"{topic} en Médecine Traditionnelle Chinoise"),
                content=article_content,
                seo=seo_data,
                word_count=word_count,
                reading_time=self._estimate_reading_time(word_count),
                last_updated=datetime.now().strftime("%Y-%m-%d"),
                categories=response.get('metadata', {}).get('categories', ["Médecine Traditionnelle Chinoise"]),
                tags=response.get('metadata', {}).get('tags', [topic, "MTC", "santé naturelle"])
            )
            
            # Conversion en dictionnaire pour le retour
            result = {
                'status': 'success',
                'article': blog_post.content,
                'metadata': {
                    'title': blog_post.title,
                    'word_count': blog_post.word_count,
                    'reading_time': blog_post.reading_time,
                    'last_updated': blog_post.last_updated,
                    'categories': blog_post.categories,
                    'tags': blog_post.tags,
                    'seo': {
                        'meta_title': blog_post.seo.meta_title,
                        'meta_description': blog_post.seo.meta_description,
                        'focus_keyword': blog_post.seo.focus_keyword,
                        'secondary_keywords': blog_post.seo.secondary_keywords
                    }
                }
            }
            
            # Ajouter des logs pour le débogage
            logger.info(f"Article généré avec succès. Titre: {blog_post.title}, Mots: {blog_post.word_count}")
            return result
            
        except Exception as e:
            logger.error(f"Erreur lors de la rédaction de l'article: {str(e)}")
            return {
                'status': 'error',
                'message': f"Erreur lors de la rédaction de l'article: {str(e)}"
            }
