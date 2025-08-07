from .base_agent import BaseAgent
from typing import Dict, Any, List, Optional
import json
import logging
import os
from datetime import datetime, time
from enum import Enum

logger = logging.getLogger(__name__)

class PostType(str, Enum):
    CONCEPT = "concept"
    INTERACTION = "interaction"
    TIP = "astuce"
    QUOTE = "citation"
    NEWS = "actualite"

class SocialCreatorAgent(BaseAgent):
    """
    Agent spécialisé dans la création de contenu Facebook pour la Médecine Traditionnelle Chinoise.
    Crée 2 publications quotidiennes optimisées pour l'engagement.
    """
    
    def __init__(self, model: str = None):
        default_model = os.getenv('DEFAULT_MODEL', 'qwen/qwen3-coder')
        super().__init__(
            name="Facebook Content Creator",
            model=model or default_model
        )
        self.platform = "facebook"
        self.post_types = [PostType.CONCEPT, PostType.INTERACTION, PostType.TIP, PostType.QUOTE, PostType.NEWS]
    
    def generate_prompt(self, input_data: Dict[str, Any]) -> str:
        """
        Génère le prompt pour la création de publications Facebook.
        
        Args:
            input_data: Doit contenir 'contenu_article' (dict) avec les clés :
                - titre (str)
                - points_cles (List[str])
                - concepts_cles (List[str])
                - citations (List[str])
                - conseils_pratiques (List[str])
        """
        contenu = input_data.get('contenu_article', {})
        
        return f"""
        # INSTRUCTIONS POUR LA CRÉATION DE PUBLICATIONS FACEBOOK MTC
        
        ## CONTEXTE
        Tu es un expert en création de contenu Facebook spécialisé en Médecine Traditionnelle Chinoise (MTC).
        
        ## MISSION
        Crée 2 publications Facebook quotidiennes basées sur le contenu fourni.
        
        ## CONTENU SOURCE
        Titre : {contenu.get('titre', 'Médecine Traditionnelle Chinoise')}
        Concepts clés : {', '.join(contenu.get('concepts_cles', []))}
        Points importants : {', '.join(contenu.get('points_cles', []))}
        Citations : {contenu.get('citations', [])}
        Conseils pratiques : {contenu.get('conseils_pratiques', [])}
        
        ## DIRECTIVES DE CRÉATION
        
        1. PUBLICATION 1 (Matin - 9h) :
           - Type : Concept/Technique spécifique
           - Objectif : Éduquer et informer
           - Ton : Professionnel mais accessible
           
        2. PUBLICATION 2 (Après-midi - 17h) :
           - Type : Question interactive OU Astuce pratique
           - Objectif : Engager la communauté
           - Ton : Conversationnel et engageant
        
        ## EXIGENCES COMMUNES
        - Longueur : 100-200 mots par publication
        - Inclure 3-5 hashtags pertinents
        - Utiliser 1-2 émojis maximum
        - Ajouter un appel à l'action clair
        - Proposer des suggestions visuelles
        
        ## EXEMPLES DE STRUCTURE
        
        Publication 1 (Concept) :
        "Saviez-vous que [concept MTC] ? 🌿
        
        [Explication simple et claire en 2-3 phrases]
        
        💡 Pourquoi c'est important ? [Bénéfice principal]
        
        👉 [Appel à l'action] Dites-moi en commentaire si vous connaissiez ce concept !
        
        #MTC #MedecineChinoise #[Concept]"
        
        Publication 2 (Interaction/Astuce) :
        "❓ [Question ouverte sur un aspect pratique de la MTC]
        
        [Contexte en 1-2 phrases si nécessaire]
        
        💬 Partagez votre expérience en commentaire !
        
        #MTC #AstuceSante #[MotClé]"
        
        ## FORMAT DE SORTIE (JSON)
        {{
            "publications": [
                {{
                    "type": "concept | interaction | astuce | citation | actualite",
                    "horaire": "09:00 | 17:00",
                    "texte": "Texte de la publication avec émojis",
                    "hashtags": ["#MTC", "#SanteNaturelle", ...],
                    "appel_action": "Phrase incitant à l'engagement",
                    "suggestions_visuelles": ["Description image 1", "Description image 2"],
                    "objectif": "Résumé en 1 phrase de l'objectif de la publication"
                }}
            ]
        }}
        """
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """
        Parse la réponse du modèle en JSON et valide la structure.
        
        Args:
            response: Réponse brute du modèle
            
        Returns:
            Dict: Données structurées des publications ou erreur
        """
        try:
            # Nettoyage de la réponse pour extraire uniquement le JSON
            start = response.find('{')
            end = response.rfind('}') + 1
            if start == -1 or end == 0:
                logger.warning("Aucun JSON trouvé dans la réponse, utilisation des publications par défaut")
                return self._generate_default_posts()
                
            json_str = response[start:end]
            data = json.loads(json_str)
            
            # Validation de base de la structure
            if 'publications' not in data or not isinstance(data['publications'], list):
                raise ValueError("Format de réponse invalide: 'publications' manquant ou invalide")
                
            # Validation de chaque publication
            required_fields = ['type', 'horaire', 'texte', 'hashtags', 'appel_action', 'suggestions_visuelles', 'objectif']
            for pub in data['publications']:
                if not all(field in pub for field in required_fields):
                    missing = [f for f in required_fields if f not in pub]
                    raise ValueError(f"Publication invalide: champs manquants {missing}")
                    
            return data
            
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Erreur lors du parsing de la réponse: {str(e)}")
            logger.warning("Utilisation des publications par défaut")
            return self._generate_default_posts()
    
    def _generate_default_posts(self, theme: str = "Médecine Traditionnelle Chinoise") -> Dict[str, Any]:
        """
        Génère des publications Facebook par défaut en cas d'erreur.
        
        Args:
            theme: Thème principal pour les publications
            
        Returns:
            Dict: Publications par défaut au format attendu
        """
        return {
            "publications": [
                {
                    "type": PostType.CONCEPT,
                    "horaire": "09:00",
                    "texte": (
                        "Découvrez les bases de l'énergie vitale (Qi) en MTC ! 🌿\n\n"
                        "Le Qi est le concept fondamental de la médecine chinoise, représentant l'énergie vitale qui "
                        "circule dans notre corps. En équilibrant cette énergie, on peut améliorer sa santé globale.\n\n"
                        "💡 Pourquoi c'est important ? Comprendre le Qi aide à prévenir les déséquilibres énergétiques.\n\n"
                        "👉 Connaissiez-vous ce concept ? Dites-le nous en commentaire !"
                    ),
                    "hashtags": ["#MTC", "#EnergieVitale", "#SanteNaturelle", "#MedecineChinoise"],
                    "appel_action": "Partagez votre expérience avec le Qi en commentaire !",
                    "suggestions_visuelles": [
                        "Illustration des méridiens énergétiques du corps humain",
                        "Personne en position de Qi Gong dans un cadre naturel"
                    ],
                    "objectif": "Éduquer sur le concept de base du Qi en MTC"
                },
                {
                    "type": PostType.INTERACTION,
                    "horaire": "17:00",
                    "texte": (
                        "❓ Quelle est votre technique de MTC préférée pour vous détendre ?\n\n"
                        "Acupuncture, Qi Gong, phytothérapie ou autre ? 💆‍♀️\n\n"
                        "💬 Partagez vos expériences en commentaire, nous sommes curieux de vous lire !"
                    ),
                    "hashtags": ["#MTC", "#BienEtre", "#SanteNaturelle", "#CommunautéMTC"],
                    "appel_action": "Réagissez avec un 👍 et partagez votre technique préférée !",
                    "suggestions_visuelles": [
                        "Personne détendue après une séance d'acupuncture",
                        "Groupe pratiquant le Tai Chi dans un parc"
                    ],
                    "objectif": "Engager la communauté dans un échange sur les pratiques de MTC"
                }
            ]
        }
        
    async def create_posts(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crée des publications Facebook à partir du contenu fourni.
        
        Args:
            content_data: Dictionnaire contenant les données du contenu source avec les clés :
                - titre (str): Titre du contenu
                - points_cles (List[str]): Points clés du contenu
                - concepts_cles (List[str]): Concepts clés de MTC
                - citations (List[str]): Citations intéressantes
                - conseils_pratiques (List[str]): Conseils pratiques liés au contenu
                
        Returns:
            Dict: Contient les publications générées ou un message d'erreur
        """
        try:
            # Préparation des données pour le prompt
            input_data = {
                'contenu_article': {
                    'titre': content_data.get('titre', 'Médecine Traditionnelle Chinoise'),
                    'points_cles': content_data.get('points_cles', []),
                    'concepts_cles': content_data.get('concepts_cles', []),
                    'citations': content_data.get('citations', []),
                    'conseils_pratiques': content_data.get('conseils_pratiques', [])
                }
            }
            
            # Génération du prompt et appel au modèle
            prompt = self.generate_prompt(input_data)
            logger.info("Génération des publications Facebook...")
            
            # Appel au modèle avec gestion des erreurs
            response = await self.process({'content': prompt})
            if not response or 'error' in response:
                logger.warning("Erreur lors de l'appel au modèle, utilisation des publications par défaut")
                return self._generate_default_posts(content_data.get('titre', 'Médecine Traditionnelle Chinoise'))
                
            # La réponse est déjà un dictionnaire parsé par BaseAgent
            publications = response.get('publications', [])

            # Journalisation pour le débogage
            logger.info(f"Publications générées avec succès: {len(publications)} publications")
            
            return publications           
        except Exception as e:
            logger.error(f"Erreur lors de la création des publications: {str(e)}", exc_info=True)
            return {
                "error": "Une erreur est survenue lors de la génération des publications",
                "details": str(e),
                "publications": self._generate_default_posts(content_data.get('titre', 'Médecine Traditionnelle Chinoise'))
            }
