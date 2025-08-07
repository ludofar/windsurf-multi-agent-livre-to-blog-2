from .base_agent import BaseAgent
from typing import Dict, Any
import PyPDF2
import logging
import os
import json

logger = logging.getLogger(__name__)

class PDFAnalyzerAgent(BaseAgent):
    """Agent spécialisé dans l'analyse des fichiers PDF de MTC"""
    
    def __init__(self, model: str = None):
        default_model = os.getenv('DEFAULT_MODEL', 'qwen/qwen3-coder')
        super().__init__(
            name="PDF Analyzer",
            model=model or default_model  # Utilisation du modèle passé en paramètre ou de DEFAULT_MODEL
        )
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extrait le texte d'un fichier PDF"""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            logger.info(f"Texte extrait avec succès du PDF: {file_path}")
            return text
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction du PDF: {str(e)}")
            raise
            
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Méthode principale pour traiter les données d'entrée.
        Implémentation de la méthode abstraite de BaseAgent.
        """
        if 'pdf_path' not in input_data:
            raise ValueError("Le chemin du PDF est requis dans input_data")
            
        return await self.analyze_pdf(input_data['pdf_path'])
        
    async def analyze_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """
        Analyse un fichier PDF et retourne les résultats structurés.
        
        Args:
            pdf_path: Chemin vers le fichier PDF à analyser
            
        Returns:
            Dict contenant les résultats de l'analyse avec une clé 'resume'
        """
        try:
            # Vérifier que le fichier existe
            if not os.path.isfile(pdf_path):
                raise FileNotFoundError(f"Le fichier PDF n'existe pas: {pdf_path}")
                
            logger.info(f"Début de l'analyse du PDF: {pdf_path}")
            
            # 1. Extraction du texte brut
            try:
                text_content = self.extract_text_from_pdf(pdf_path)
                if not text_content.strip():
                    raise ValueError("Le fichier PDF est vide ou n'a pas pu être lu correctement")
            except Exception as e:
                logger.error(f"Erreur lors de l'extraction du texte du PDF: {str(e)}")
                raise
            
            # 2. Préparation des données pour l'analyse
            analysis_input = {
                'pdf_path': str(pdf_path),  # S'assurer que c'est une chaîne
                'content': text_content[:10000],  # Limite pour éviter les tokens excessifs
                'filename': os.path.basename(pdf_path)
            }
            
            # 3. Génération du prompt d'analyse
            prompt = self.generate_prompt(analysis_input)
            
            # 4. Appel au modèle de langage via la méthode de base
            try:
                result = await super().process({'content': prompt})
            except Exception as e:
                logger.error(f"Erreur lors de l'appel au modèle: {str(e)}")
                raise
            
            # 5. Traitement de la réponse
            try:
                # Essayer de parser la réponse comme du JSON
                if isinstance(result, dict):
                    analysis_result = result
                else:
                    try:
                        analysis_result = json.loads(str(result))
                    except (json.JSONDecodeError, TypeError) as e:
                        logger.warning(f"La réponse n'est pas au format JSON valide: {str(e)}")
                        analysis_result = {
                            'resume': str(result)[:1000],  # Limiter la taille
                            'status': 'warning',
                            'message': 'Le format de la réponse est inattendu, utilisation du texte brut comme résumé'
                        }
            except Exception as e:
                logger.error(f"Erreur lors du traitement de la réponse: {str(e)}")
                analysis_result = {
                    'resume': f"Erreur lors de l'analyse du PDF: {str(e)}",
                    'status': 'error',
                    'message': str(e)
                }
            
            # 6. S'assurer que la clé 'resume' existe
            if 'resume' not in analysis_result:
                analysis_result['resume'] = analysis_result.get('message', 'Aucun résumé généré')
            
            # 7. Ajout des métadonnées
            analysis_result['metadata'] = {
                'pdf_path': pdf_path,
                'pages_analyzed': len(text_content.split('\f')),
                'chars_analyzed': len(text_content)
            }
            
            logger.info(f"Analyse du PDF {pdf_path} terminée avec succès")
            return analysis_result
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse du PDF {pdf_path}: {str(e)}")
            return {
                'resume': f'Erreur lors de l\'analyse du PDF: {str(e)}',
                'status': 'error',
                'message': str(e),
                'pdf_path': pdf_path
            }
    
    def generate_prompt(self, input_data: Dict[str, Any]) -> str:
        """
        Génère un prompt optimisé pour l'analyse de documents MTC.
        
        Args:
            input_data: Doit contenir 'content' (texte extrait du PDF) et 'pdf_path' (chemin du fichier)
            
        Returns:
            str: Le prompt optimisé pour l'analyse du PDF
        """
        # Limiter la taille du texte d'entrée pour éviter les dépassements de contexte
        max_text_length = 15000  # Réduit de 20k à 15k pour laisser plus d'espace pour la réponse
        pdf_text = input_data.get('content', '')[:max_text_length]
        pdf_path = input_data.get('pdf_path', 'fichier_inconnu')
        
        # Structure du prompt optimisé
        return f"""
        # Analyse de Document MTC - Format Réponse Structurée
        
        ## Contexte
        - Fichier: {pdf_path}
        - Tâche: Analyser et structurer le contenu MTC
        - Format de sortie: JSON structuré (voir ci-dessous)
        
        ## Instructions d'Analyse
        1. **Structure**
           - Identifier chapitres et sections
           - Noter la progression logique
           - Repérer les transitions clés
           
        2. **Contenu MTC**
           - Extraire théories fondamentales (Qi, Yin/Yang, 5 Éléments)
           - Noter méridiens et points d'acupuncture
           - Lister méthodes de diagnostic et traitements
           - Identifier plantes et formules médicinales
           - Relever principes de diététique/prévention
        
        ## Texte Source (extrait)
        {pdf_text}{'\n[Texte tronqué - analysez cette partie en priorité]' if len(pdf_text) >= max_text_length else ''}
        
        ## Format de Réponse (JSON)
        {{
          "metadonnees": {{
            "titre": "Titre du document",
            "auteur": "Nom de l'auteur si disponible",
            "annee": "Année de publication si disponible"
          }},
          "resume_global": "Résumé concis (3-5 phrases)",
          "concepts_cles": ["concept1", "concept2", "..."],
          "structure": [
            {{
              "type": "chapitre|section",
              "titre": "Titre",
              "resume": "Résumé",
              "concepts": ["concept1", "..."]
            }}
          ]
        }}
        
        ## Notes Importantes
        - Soyez concis et précis
        - Ne pas inventer d'information
        - Privilégier la qualité à la quantité
        - Si le texte est incomplet, l'indiquer dans le résumé
        """
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """
        Parse et valide la réponse du modèle en JSON
        
        Args:
            response: Réponse brute du modèle sous forme de chaîne de caractères
            
        Returns:
            Dict[str, Any]: Dictionnaire Python contenant les données structurées
            
        Raises:
            json.JSONDecodeError: Si le JSON n'est pas valide
            ValueError: Si la structure des données ne correspond pas au format attendu
        """
        try:
            # Nettoyage de la réponse pour extraire uniquement le JSON
            start = response.find('{')
            end = response.rfind('}') + 1
            
            if start == -1 or end == 0:
                raise json.JSONDecodeError("Aucun JSON trouvé dans la réponse", doc=response, pos=0)
                
            json_str = response[start:end].strip()
            
            # Validation de base du JSON
            data = json.loads(json_str)
            
            # Validation de la structure minimale
            required_sections = ['metadonnees', 'structure']
            for section in required_sections:
                if section not in data:
                    raise ValueError(f"Section requise manquante: {section}")
            
            # Validation des métadonnées minimales
            required_metadata = ['titre_livre']
            for field in required_metadata:
                if field not in data['metadonnees']:
                    raise ValueError(f"Champ de métadonnées requis manquant: {field}")
            
            # Validation de la structure des chapitres
            if not isinstance(data['structure'], list):
                raise ValueError("La structure doit être une liste de chapitres")
                
            for chapitre in data['structure']:
                if not all(k in chapitre for k in ['chapitre', 'resume', 'sections']):
                    raise ValueError("Chaque chapitre doit contenir 'chapitre', 'resume' et 'sections'")
                
                for section in chapitre['sections']:
                    if not all(k in section for k in ['titre', 'contenu_cle', 'concepts_importants']):
                        raise ValueError("Chaque section doit contenir 'titre', 'contenu_cle' et 'concepts_importants'")
            
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"Erreur lors du parsing de la réponse JSON: {str(e)}")
            logger.debug(f"Réponse problématique: {response}")
            raise
        except Exception as e:
            logger.error(f"Erreur lors de la validation de la structure des données: {str(e)}")
            raise
            return {"error": "Erreur lors de l'analyse de la réponse"}
