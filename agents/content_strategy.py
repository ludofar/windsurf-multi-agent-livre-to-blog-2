from .base_agent import BaseAgent
from typing import Dict, Any, List, Optional, TypedDict
from enum import Enum, auto
import json
import logging
import os
import re
from datetime import datetime, timedelta
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, TypedDict

from agents.theme_manager import ThemeAnalysis

logger = logging.getLogger(__name__)

class ContentType(str, Enum):
    ARTICLE_BLOG = "article_blog"
    POST_FACEBOOK = "post_facebook"
    INFOGRAPHIC = "infographic"
    NEWSLETTER = "newsletter"
    VIDEO = "video"
    PODCAST = "podcast"

class AudienceType(str, Enum):
    BEGINNERS = "débutants"
    ENTHUSIASTS = "passionnés"
    PRACTITIONERS = "praticiens"
    THERAPISTS = "thérapeutes"
    GENERAL = "grand_public"

@dataclass
class ContentPiece:
    title: str
    content_type: ContentType
    target_audience: List[AudienceType]
    seo_keywords: List[str]
    tone: str
    engagement_elements: List[str]
    estimated_length: Optional[int] = None
    structure: Optional[List[str]] = None

class ContentStrategyAgent(BaseAgent):
    """
    Agent responsable de la stratégie éditoriale avancée pour la MTC.
    Développe des plans de contenu complets basés sur l'analyse des données.
    """
    
    def __init__(self, model: str = None):
        default_model = os.getenv('DEFAULT_MODEL', 'qwen/qwen3-coder')
        super().__init__(
            name="Content Strategy Agent",
            model=model or default_model
        )
        
    async def generate_strategy(self, analysis: Dict[str, Any], theme_analysis: ThemeAnalysis) -> Dict[str, Any]:
        """
        Génère une stratégie de contenu basée sur l'analyse fournie.
        
        Args:
            analysis: Résultat de l'analyse du PDF
            theme_analysis: Analyse thématique du contenu (objet ThemeAnalysis)
            
        Returns:
            Un dictionnaire contenant la stratégie générée
        """
        content_type = 'article_blog'  # Définition de la variable content_type
        
        try:
            # Extraire le contenu de l'analyse
            content = analysis.get('resume', 'Aucun contenu disponible')
            
            prompt = self.generate_prompt({
                'content': content,
                'content_type': content_type,
                'task': 'generate_strategy',
                'analysis': analysis,
                'theme_analysis': asdict(theme_analysis)  # Convertir l'objet en dictionnaire
            })
            
            response = await self.process({'content': prompt})
            
            # Traitement de la réponse
            strategy = self._parse_response(response, content_type)
            
            # S'assurer que les champs essentiels sont présents
            if 'title' not in strategy:
                strategy['title'] = f"Stratégie pour {content_type}"
                
            if 'content_type' not in strategy:
                strategy['content_type'] = content_type
                
            return strategy
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération de la stratégie: {str(e)}", exc_info=True)
            # Retourner une stratégie par défaut en cas d'erreur
            return self._generate_default_strategy(content_type)
            
    def _parse_response(self, response: Any, content_type: str = None) -> Dict[str, Any]:
        """
        Parse et valide la réponse du modèle en JSON selon la structure attendue.
        
        Args:
            response: Réponse brute du modèle sous forme de chaîne de caractères ou de dict
            content_type: Type de contenu pour les valeurs par défaut (optionnel)
            
        Returns:
            Dict[str, Any]: Dictionnaire Python contenant la stratégie de contenu structurée
            
        Raises:
            json.JSONDecodeError: Si le JSON n'est pas valide
            ValueError: Si la structure des données ne correspond pas au format attendu
        """
        # Si la réponse est déjà un dictionnaire, on la retourne directement
        if isinstance(response, dict):
            return response
            
        # Conversion en chaîne si nécessaire
        response_text = str(response)
        
        # Nettoyage de la réponse
        response_text = response_text.strip()
        
        # Liste des tentatives de parsing
        parsing_attempts = [
            # Tentative 1: Parser directement comme JSON
            lambda s: json.loads(s),
            
            # Tentative 2: Extraire le JSON entre accolades
            lambda s: json.loads(s[s.find('{'):s.rfind('}')+1]),
            
            # Tentative 3: Remplacer les guillemets simples par des doubles
            lambda s: json.loads(s.replace("'", '"')),
            
            # Tentative 4: Nettoyer les caractères non-ASCII
            lambda s: json.loads(''.join(c for c in s if ord(c) < 128 or c.isspace())),
            
            # Tentative 5: Remplacer les guillemets simples par des doubles et nettoyer
            lambda s: json.loads(re.sub(r"(?<!\\)(?:\\)*'", '"', s).replace('\\"', "'"))
        ]
        
        # Essayer chaque méthode de parsing
        for i, parse_attempt in enumerate(parsing_attempts, 1):
            try:
                data = parse_attempt(response_text)
                # Valider la structure des données
                return self._validate_strategy_structure(data, content_type)
            except (json.JSONDecodeError, ValueError, SyntaxError) as e:
                logger.debug(f"Tentative de parsing {i} échouée: {str(e)}")
                continue
        
        # Si tout échoue, retourner une structure par défaut avec le contenu brut
        logger.warning("Échec de toutes les tentatives de parsing, utilisation du contenu brut")
        return self._generate_default_strategy(content_type or 'article_blog')
    
    def _validate_strategy_structure(self, data: Dict[str, Any], content_type: str = None) -> Dict[str, Any]:
        """
        Valide la structure de la stratégie de contenu et ajoute des valeurs par défaut si nécessaire.
        
        Args:
            data: Données à valider
            content_type: Type de contenu pour les valeurs par défaut
            
        Returns:
            Dict[str, Any]: Données validées avec des valeurs par défaut si nécessaire
        """
        # Assurer que les sections obligatoires existent
        if 'analyse_strategique' not in data:
            data['analyse_strategique'] = {}
            
        if 'plan_contenu' not in data:
            data['plan_contenu'] = {}
            
        if 'calendrier_editorial' not in data:
            data['calendrier_editorial'] = []
            
        if 'metriques_succes' not in data:
            data['metriques_succes'] = {}
            
        # Ajouter des valeurs par défaut pour les thèmes prioritaires si nécessaire
        if 'themes_prioritaires' not in data['analyse_strategique']:
            data['analyse_strategique']['themes_prioritaires'] = [
                {
                    'theme': 'Thème par défaut',
                    'potentiel_trafic': 'moyen',
                    'concurrence': 'moyenne',
                    'angles': ['Angle par défaut'],
                    'personas_cibles': ['grand public']
                }
            ]
            
        # S'assurer qu'il y a au moins un article de blog suggéré
        if 'articles_blog' not in data['plan_contenu'] or not data['plan_contenu']['articles_blog']:
            data['plan_contenu']['articles_blog'] = [
                {
                    'titre': 'Article sur la MTC',
                    'public_cible': 'grand public',
                    'mots_cles': ['MTC', 'santé naturelle'],
                    'ton': 'informatif',
                    'structure': ['Introduction', 'Développement', 'Conclusion'],
                    'elements_engagement': ['Question au lecteur'],
                    'longueur_estimee': 1500
                }
            ]
            
        # Ajouter des sujets suggérés pour le blog writer
        data['suggested_topics'] = [
            topic['theme'] 
            for topic in data['analyse_strategique'].get('themes_prioritaires', [])
        ] or ['Médecine Traditionnelle Chinoise']
        
        # Ajouter le type de contenu
        if content_type:
            data['content_type'] = content_type
            
        return data
    
    def _generate_default_calendar(self, themes: List[str]) -> Dict[str, Any]:
        """Génère un calendrier éditorial par défaut basé sur les thèmes principaux"""
        from datetime import datetime, timedelta
        
        start_date = datetime.now()
        calendar = {}
        
        for i, theme in enumerate(themes[:4]):  # Limiter à 4 thèmes pour l'exemple
            date_key = (start_date + timedelta(days=i*7)).strftime("%Y-%m-%d")
            calendar[date_key] = {
                'theme': theme,
                'content_type': 'article_blog',
                'status': 'planned'
            }
            
        return calendar
    
    def _generate_default_strategy(self, content_type: str) -> Dict[str, Any]:
        """Génère une stratégie par défaut en cas d'erreur"""
        return {
            'title': f'Stratégie pour {content_type}',
            'content_type': content_type,
            'status': 'default',
            'message': 'Stratégie générée par défaut en raison d\'une erreur',
            'suggested_topics': ['Médecine Traditionnelle Chinoise'],
            'analyse_strategique': {
                'themes_prioritaires': [
                    {
                        'theme': 'Introduction à la MTC',
                        'potentiel_trafic': 'élevé',
                        'concurrence': 'moyenne',
                        'angles': ['Découverte', 'Bases', 'Bienfaits'],
                        'personas_cibles': ['débutant', 'grand public']
                    }
                ]
            },
            'plan_contenu': {
                'articles_blog': [
                    {
                        'titre': 'Introduction à la Médecine Traditionnelle Chinoise',
                        'public_cible': 'débutant',
                        'mots_cles': ['MTC', 'santé naturelle', 'médecine chinoise'],
                        'ton': 'informatif',
                        'structure': ['Introduction', 'Histoire', 'Concepts clés', 'Conclusion'],
                        'elements_engagement': ['Question au lecteur'],
                        'longueur_estimee': 1500
                    }
                ]
            },
            'plan': {
                'objectifs': ['Informer', 'Éduquer', 'Engager'],
                'public_cible': 'grand public',
                'ton': 'professionnel',
                'frequence_publication': 'hebdomadaire'
            }
        }
        
        # Paramètres de base pour la stratégie
        self.default_publication_frequency = {
            ContentType.ARTICLE_BLOG: 2,  # par semaine
            ContentType.POST_FACEBOOK: 10,  # par semaine
            ContentType.INFOGRAPHIC: 1,  # par semaine
            ContentType.NEWSLETTER: 1,  # par semaine
            ContentType.VIDEO: 1,  # toutes les 2 semaines
            ContentType.PODCAST: 1  # par mois
        }
    
    def generate_prompt(self, input_data: Dict[str, Any]) -> str:
        """
        Génère le prompt pour la création d'une stratégie de contenu avancée.
        
        Args:
            input_data: Doit contenir 'themes', 'concepts' et 'structure' du livre
            
        Returns:
            str: Prompt détaillé pour l'analyse stratégique
        """
        themes = input_data.get('themes', [])
        concepts = input_data.get('concepts', [])
        structure = input_data.get('structure', [])
        
        return f"""
        Tu es un expert en stratégie de contenu pour la Médecine Traditionnelle Chinoise (MTC) 
        avec une expertise en marketing digital et référencement.
        
        CONTEXTE :
        - Public cible : Professionnels de santé, praticiens MTC, étudiants et grand public intéressé
        - Objectif : Éduquer, informer et engager la communauté autour de la MTC
        - Ton : Professionnel mais accessible, précis mais pas trop technique
        
        DONNÉES D'ENTRÉE :
        - Thèmes principaux : {json.dumps(themes[:10], ensure_ascii=False, indent=2)}
        - Concepts clés : {json.dumps(concepts[:20], ensure_ascii=False, indent=2)}
        - Structure du livre : {json.dumps(structure[:3], ensure_ascii=False, indent=2)}...
        
        TÂCHES DÉTAILLÉES :
        
        1. ANALYSE STRATÉGIQUE
           - Identifie les 3-5 sujets principaux avec le plus grand potentiel de trafic
           - Propose des angles uniques pour aborder chaque thème
           - Définis des personas cibles (débutants, praticiens, etc.)
           
        2. PLAN DE CONTENU DÉTAILLÉ
           Pour chaque contenu proposé, précise :
           - Titre accrocheur et optimisé SEO
           - Public cible spécifique
           - Mots-clés principaux et secondaires
           - Ton et style d'écriture
           - Éléments d'engagement (questions, appels à l'action)
           
        3. CALENDRIER ÉDITORIAL SUR 30 JOURS
           - Équilibre entre différents types de contenu
           - Variations de sujets et de formats
           - Moments optimaux de publication
           
        4. STRATÉGIE DE DISTRIBUTION
           - Canaux recommandés pour chaque type de contenu
           - Stratégie de republication et de promotion
           - Collaboration avec influenceurs et experts
        
        FORMAT DE SORTIE (JSON) :
        {{
            "analyse_strategique": {{
                "themes_prioritaires": [
                    {{
                        "theme": "thème",
                        "potentiel_trafic": "élevé/moyen/faible",
                        "concurrence": "élevée/moyenne/faible",
                        "angles": ["angle1", "angle2"],
                        "personas_cibles": ["débutant", "praticien"]
                    }}
                ]
            }},
            "plan_contenu": {{
                "articles_blog": [
                    {{
                        "titre": "Titre optimisé SEO",
                        "public_cible": "débutant/praticien/expert",
                        "mots_cles": ["mot1", "mot2"],
                        "ton": "informatif/éducatif/conversationnel",
                        "structure": ["section1", "section2"],
                        "elements_engagement": ["question", "CTA"],
                        "longueur_estimee": 1500
                    }}
                ],
                "reseaux_sociaux": {{
                    "strategie_globale": "...",
                    "publications_quotidiennes": [
                        {{
                            "plateforme": "facebook/instagram/linkedin",
                            "type_contenu": "astuce/citation/infographie",
                            "horaire_suggere": "HH:MM",
                            "exemple_texte": "...",
                            "hashtags": ["#MTC", "#SanteNaturelle"]
                        }}
                    ]
                }}
            }},
            "calendrier_editorial": [
                {{
                    "date": "YYYY-MM-DD",
                    "contenus": [
                        {{
                            "type": "article_blog/post_facebook/infographic",
                            "titre": "Titre du contenu",
                            "statut": "rédaction/relecture/publication",
                            "responsable": "rédacteur/designer"
                        }}
                    ]
                }}
            ],
            "metriques_succes": {{
                "kpis": ["trafic", "temps_session", "partages"],
                "objectifs": {{
                    "taux_engagement": ">3%",
                    "taux_conversion": ">2%"
                }}
            }}
        }}
        """
    

    
    def _generate_default_calendar(self, themes: List[str]) -> List[Dict]:
        """Génère un calendrier éditorial par défaut basé sur les thèmes"""
        calendar = []
        start_date = datetime.now()
        
        for i in range(28):  # 4 semaines
            current_date = start_date + timedelta(days=i)
            content_type = self.default_content_types[i % len(self.default_content_types)]
            theme = themes[i % len(themes)]
            
            calendar.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "type_contenu": content_type,
                "titre": f"Contenu sur {theme}",
                "description": f"Description à définir pour le contenu sur {theme}",
                "mots_cles": [theme.lower(), "MTC", "santé naturelle"],
                "objectif": "Informer et engager la communauté sur les bienfaits de la MTC"
            })
        
        return calendar
