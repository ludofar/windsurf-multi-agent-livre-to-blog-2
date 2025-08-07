from .base_agent import BaseAgent
from typing import Dict, Any, List, Set, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import logging
import os
import re
import ast
from datetime import datetime, timedelta
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)

class ContentType(str, Enum):
    ARTICLE = "article_blog"
    SOCIAL_MEDIA = "reseau_social"
    NEWSLETTER = "newsletter"
    GUIDE = "guide_pratique"
    VIDEO = "video"

@dataclass
class ThemeAnalysis:
    """Résultat d'analyse thématique d'un contenu."""
    main_theme: str
    sub_themes: List[str] = field(default_factory=list)
    key_concepts: List[str] = field(default_factory=list)
    mtc_terms: Dict[str, int] = field(default_factory=dict)
    repetitions: Dict[str, int] = field(default_factory=dict)
    related_content: List[Dict[str, str]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    content_gaps: List[str] = field(default_factory=list)
    publication_schedule: Optional[Dict[str, Any]] = None

class ThemeManagerAgent(BaseAgent):
    """
    Agent responsable de la cohérence thématique globale du contenu MTC.
    
    Fonctionnalités clés :
    - Détection des répétitions et redondances
    - Suivi des concepts et termes MTC
    - Planification de la progression thématique
    - Recommandations d'ajustement
    """
    
    def __init__(self, model: str = None):
        default_model = os.getenv('DEFAULT_MODEL', 'qwen/qwen3-coder')
        super().__init__(
            name="Theme Manager",
            model=model or default_model
        )
        
        # Initialisation des attributs de la base de connaissances thématique
        self.theme_history = set()  # Thèmes principaux déjà traités
        self.used_terms = Counter()  # Termes et leur fréquence d'utilisation
        self.content_registry = []   # Référence à tous les contenus créés
        self.concept_network = defaultdict(set)  # Relations entre concepts
        self.publication_calendar = {}  # Calendrier de publication
        self.mtc_glossary = self._load_mtc_glossary()  # Glossaire des termes MTC
        
    async def call_model(self, prompt: str) -> str:
        """
        Appelle le modèle de langage avec le prompt fourni.
        
        Args:
            prompt: Le prompt à envoyer au modèle
            
        Returns:
            La réponse textuelle du modèle
        """
        try:
            response = await self.process({'content': prompt})
            if isinstance(response, dict):
                return response.get('response', str(response))
            return str(response)
        except Exception as e:
            logger.error(f"Erreur lors de l'appel au modèle: {str(e)}")
            raise
    
    def _load_mtc_glossary(self) -> Set[str]:
        """Charge le glossaire des termes MTC depuis un fichier ou une ressource."""
        # À implémenter : charger depuis un fichier JSON ou une base de données
        return {
            # Théories fondamentales
            'yin_yang', 'wu_xing', 'qi', 'jing', 'shen', 'xue', 'jing_luo', 'zang_fu',
            # Diagnostics
            'observation', 'auscultation', 'interrogatoire', 'palpation', 'pouls', 'langue',
            # Techniques de traitement
            'acupuncture', 'pharmacopee', 'tui_na', 'qi_gong', 'dietetique', 'moxibustion',
            # Concepts clés
            'meridiens', 'points_d_acupuncture', 'organes_entrailles', 'energies_perverses',
            'symptomes', 'syndromes', 'therapie', 'prevention', 'equilibre'
        }

    def _extract_key_terms(self, text: str) -> List[Tuple[str, int]]:
        """Extrait les termes clés MTC d'un texte avec leur fréquence."""
        words = re.findall(r'\b[\w-]+\b', text.lower())
        mtc_terms = [word for word in words if word in self.mtc_glossary]
        return Counter(mtc_terms).most_common()

    def _find_repetitions(self, text: str) -> Dict[str, int]:
        """Identifie les répétitions excessives de termes."""
        words = re.findall(r'\b[\w-]+\b', text.lower())
        word_counts = Counter(words)
        return {word: count for word, count in word_counts.items() 
                if count > 5 and len(word) > 3}  # Seuil arbitraire

    def generate_prompt(self, input_data: Dict[str, Any]) -> str:
        """
        Génère le prompt pour l'analyse de cohérence thématique avancée.
        
        Args:
            input_data: Doit contenir 'content' (texte à analyser) et 'content_type'.
            
        Returns:
            str: Prompt détaillé pour l'analyse thématique.
        """
        current_content = input_data.get('content', '')
        content_type = input_data.get('content_type', ContentType.ARTICLE)
        
        # Analyse préliminaire
        key_terms = self._extract_key_terms(current_content)
        repetitions = self._find_repetitions(current_content)
        
        # Récupération du contexte
        recent_themes = list(self.theme_history)[-10:] if self.theme_history else []
        frequent_terms = self.used_terms.most_common(20)
        
        return f"""
        # ANALYSE DE COHÉRENCE THÉMATIQUE MTC
        
        ## CONTEXTE
        Tu es un expert en Médecine Traditionnelle Chinoise chargé de maintenir 
        la cohérence thématique d'une collection de contenus éducatifs.
        
        ## MISSION
        Analyse le contenu suivant pour en évaluer la cohérence thématique 
        et proposer des améliorations.
        
        ## INFORMATIONS
        - Type de contenu: {content_type.upper()}
        - Thèmes récents: {', '.join(recent_themes) or 'Aucun thème récent'}
        - Termes fréquents: {', '.join([f"{t[0]} ({t[1]})" for t in frequent_terms]) or 'Aucun terme fréquent'}
        
        ## CONTENU À ANALYSER
        {current_content[:3000]}... [contenu tronqué si nécessaire]
        
        ## INSTRUCTIONS D'ANALYSE
        1. Identifie le thème principal et les sous-thèmes
        2. Analyse la cohérence avec les thèmes existants
        3. Détecte les répétitions et redondances
        4. Propose des liens avec d'autres contenus
        5. Recommande des ajustements pour améliorer la cohérence
        
        ## FORMAT DE SORTIE (JSON)
        {{
            "theme_principal": {{
                "nom": "nom_du_theme",
                "pertinence": "élevée/moyenne/faible",
                "description": "description du thème principal"
            }},
            "sous_themes": [
                {{
                    "nom": "sous_theme_1",
                    "pertinence": "élevée/moyenne/faible",
                    "description": "description du sous-thème"
                }}
            ],
            "repetitions": [
                {{
                    "terme": "terme_repeté",
                    "occurrences": X,
                    "alternatives": ["alt1", "alt2"],
                    "recommandation": "conseil pour réduire la redondance"
                }}
            ],
            "liens_thematiques": [
                {{
                    "type": "complementaire/approfondissement/prérequis",
                    "titre": "Titre du contenu lié",
                    "lien": "lien_ou_reference",
                    "valeur_ajoutee": "ce que ce lien apporte"
                }}
            ],
            "recommandations": [
                "recommandation 1",
                "recommandation 2"
            ],
            "plan_progression": {{
                "etapes_suivantes": ["étape 1", "étape 2"],
                "themes_complementaires": ["thème 1", "thème 2"],
                "calendrier_suggere": "suggestion de planning"
            }}
        }}
        """
    
    async def analyze_content(self, content: str, content_type: str = ContentType.ARTICLE) -> ThemeAnalysis:
        """
        Analyse un contenu pour évaluer sa cohérence thématique.
        
        Args:
            content: Le contenu à analyser
            content_type: Type de contenu (article, post, etc.)
            
        Returns:
            ThemeAnalysis: Résultats de l'analyse thématique
        """
        try:
            # Préparation des données d'entrée
            input_data = {
                'content': content,
                'content_type': content_type
            }
            
            # Génération et exécution du prompt
            prompt = self.generate_prompt(input_data)
            response = await self.call_model(prompt)
            
            # Traitement de la réponse
            if not response or 'error' in response:
                logger.warning("Erreur lors de l'appel au modèle, utilisation d'une analyse basique")
                return self._basic_analysis(content)
                
            # Extraction et validation de la réponse
            analysis_result = self._parse_response(response)
            if 'error' in analysis_result:
                logger.warning(f"Erreur d'analyse : {analysis_result['error']}")
                return self._basic_analysis(content)
            
            # Mise à jour des bases de connaissances
            self._update_knowledge_base(analysis_result, content)
            
            # Création du rapport d'analyse
            return self._create_analysis_report(analysis_result)
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse thématique : {str(e)}", exc_info=True)
            return ThemeAnalysis(
                main_theme="Inconnu",
                recommendations=["Une erreur est survenue lors de l'analyse thématique"]
            )
    
    def _parse_response(self, response: Any) -> Dict[str, Any]:
        """
        Parse et valide la réponse du modèle.
        
        Args:
            response: Réponse brute du modèle (peut être un str, un dict ou un objet JSON)
            
        Returns:
            Dict: Données structurées ou message d'erreur
        """
        # Si la réponse est déjà un dictionnaire, on la retourne directement
        if isinstance(response, dict):
            logger.debug("Réponse déjà sous forme de dictionnaire, conversion directe")
            return self._validate_and_clean_response(response)
            
        # Si la réponse est None ou vide
        if not response:
            logger.error("Réponse vide reçue du modèle")
            return {"error": "Réponse vide reçue du modèle"}
            
        # Si la réponse est une chaîne, on essaie de la parser
        if not isinstance(response, str):
            response = str(response)
            
        # Nettoyage initial de la réponse
        json_str = response.strip()
        
        # Liste des tentatives de parsing avec leurs fonctions de nettoyage
        parsing_attempts = [
            # Tentative 1: Parser directement comme JSON
            lambda s: json.loads(s),
            
            # Tentative 2: Nettoyer les caractères non-ASCII et essayer à nouveau
            lambda s: json.loads(''.join(c for c in s if ord(c) < 128 or c.isspace())),
            
            # Tentative 3: Extraire le JSON entre accolades
            lambda s: json.loads(s[s.find('{'):s.rfind('}')+1]),
            
            # Tentative 4: Remplacer les guillemets simples par des doubles
            lambda s: json.loads(s.replace("'", '"')),
            
            # Tentative 5: Utiliser ast.literal_eval pour les dictionnaires Python
            lambda s: ast.literal_eval(s),
            
            # Tentative 6: Remplacer les guillemets simples par des doubles et nettoyer
            lambda s: json.loads(re.sub(r"(?<!\\)(?:\\)*'", '"', s).replace('\\"', "'"))
        ]
        
        # Essayer chaque méthode de parsing jusqu'à ce qu'une fonctionne
        for i, parse_attempt in enumerate(parsing_attempts, 1):
            try:
                cleaned_str = json_str
                
                # Nettoyage spécifique pour chaque tentative
                if i == 3:  # Tentative 3: extraction entre accolades
                    start = cleaned_str.find('{')
                    end = cleaned_str.rfind('}') + 1
                    if start == -1 or end <= 0 or start >= end:
                        continue
                    cleaned_str = cleaned_str[start:end]
                
                # Éviter les erreurs avec les caractères non-ASCII pour les premières tentatives
                if i < 3:
                    cleaned_str = ''.join(c for c in cleaned_str if ord(c) < 128 or c.isspace())
                
                # Essayer de parser
                data = parse_attempt(cleaned_str)
                
                # Si on arrive ici, le parsing a réussi
                logger.debug(f"Parsing réussi avec la tentative {i}")
                return self._validate_and_clean_response(data)
                
            except (json.JSONDecodeError, ValueError, SyntaxError) as e:
                logger.debug(f"Tentative {i} échouée: {str(e)}")
                continue
            except Exception as e:
                logger.debug(f"Erreur inattendue lors de la tentative {i}: {str(e)}")
                continue
        
        # Si on arrive ici, toutes les tentatives ont échoué
        error_msg = "Échec de toutes les tentatives de parsing de la réponse"
        logger.error(f"{error_msg}. Début de la réponse: {json_str[:200]}...")
        
        # Retourner une réponse d'erreur structurée
        return {
            'theme_principal': {
                'nom': 'Erreur de parsing',
                'pertinence': 'inconnue',
                'description': 'Impossible d\'analyser la réponse du modèle.'
            },
            'sous_themes': [],
            'recommandations': [
                'Vérifier le format de la réponse du modèle.',
                'S\'assurer que la réponse est un JSON valide.'
            ],
            'error': error_msg,
            'response_preview': f"{json_str[:200]}..." if len(json_str) > 200 else json_str
        }
            
    def _validate_and_clean_response(self, data: Any) -> Dict[str, Any]:
        """
        Valide et nettoie la réponse du modèle.
        
        Args:
            data: Données à valider et nettoyer
            
        Returns:
            Dict: Données validées et nettoyées
        """
        try:
            # Si ce n'est pas un dictionnaire, on essaie de le convertir
            if not isinstance(data, dict):
                if hasattr(data, 'model_dump'):  # Pour les modèles Pydantic
                    data = data.model_dump()
                else:
                    data = {"response": str(data)}
            
            # Définition des champs obligatoires avec valeurs par défaut
            required_fields = {
                'theme_principal': {
                    'nom': 'Thème principal non spécifié',
                    'pertinence': 'moyenne',
                    'description': 'Aucune description fournie'
                },
                'sous_themes': [],
                'recommandations': []
            }
            
            # Vérification et ajout des champs manquants avec des valeurs par défaut
            for field, default in required_fields.items():
                if field not in data:
                    logger.warning(f"Champ manquant dans la réponse : {field}, utilisation d'une valeur par défaut")
                    data[field] = default
            
            # Validation et normalisation des types
            if isinstance(data['theme_principal'], str):
                data['theme_principal'] = {
                    'nom': data['theme_principal'],
                    'pertinence': 'moyenne',
                    'description': 'Aucune description fournie'
                }
            
            if not isinstance(data['sous_themes'], list):
                data['sous_themes'] = [str(data['sous_themes'])]
                
            if not isinstance(data['recommandations'], list):
                data['recommandations'] = [str(data['recommandations'])]
            
            # Nettoyage des valeurs None et des chaînes vides
            def clean_dict(d):
                if isinstance(d, dict):
                    return {k: clean_dict(v) for k, v in d.items() 
                           if v is not None and v != '' and not (isinstance(v, (list, dict, str)) and not v)}
                elif isinstance(d, list):
                    return [clean_dict(v) for v in d if v is not None and v != '']
                return d
            
            data = clean_dict(data)
            
            return data
            
        except Exception as e:
            logger.error(f"Erreur lors de la validation de la réponse: {str(e)}")
            # En cas d'erreur, on retourne une structure minimale valide
            return {
                'theme_principal': {
                    'nom': 'Erreur lors de l\'analyse',
                    'pertinence': 'inconnue',
                    'description': f"Une erreur est survenue: {str(e)}"
                },
                'sous_themes': [],
                'recommandations': ["Veuillez vérifier manuellement le contenu généré"]
            }
    
    def _basic_analysis(self, content: str) -> ThemeAnalysis:
        """
        Effectue une analyse basique du contenu en cas d'échec de l'analyse avancée.
        
        Args:
            content: Contenu à analyser
            
        Returns:
            ThemeAnalysis: Analyse basique du contenu
        """
        key_terms = self._extract_key_terms(content)
        repetitions = self._find_repetitions(content)
        
        # Extraction des thèmes principaux (mots-clés les plus fréquents)
        main_theme = key_terms[0][0] if key_terms else "Inconnu"
        
        # Création d'une analyse basique
        analysis = ThemeAnalysis(
            main_theme=main_theme,
            sub_themes=[term[0] for term in key_terms[1:4]],
            mtc_terms=dict(key_terms[:10]),
            repetitions=repetitions,
            recommendations=[
                "L'analyse automatique a rencontré des difficultés. Une vérification manuelle est recommandée."
            ]
        )
        
        return analysis
    
    def _update_knowledge_base(self, analysis_result: Any, content: str) -> str:
        """
        Met à jour la base de connaissances avec les résultats de l'analyse.
        
        Args:
            analysis_result: Résultats de l'analyse thématique (dict ou ThemeAnalysis)
            content: Contenu analysé
            
        Returns:
            str: ID du contenu enregistré
        """
        try:
            content_id = f"content_{len(self.content_registry) + 1}"
            
            # Gestion à la fois des dictionnaires et des objets ThemeAnalysis
            if hasattr(analysis_result, 'main_theme'):
                # C'est un objet ThemeAnalysis
                main_theme = analysis_result.main_theme
                sub_themes = analysis_result.sub_themes
            elif isinstance(analysis_result, dict):
                # C'est un dictionnaire
                main_theme = analysis_result.get('theme_principal', {}).get('nom', 'inconnu')
                sub_themes = [st.get('nom', '') for st in analysis_result.get('sous_themes', []) 
                            if isinstance(st, dict) and 'nom' in st]
            else:
                raise ValueError("Type d'analyse non supporté")
            
            # Mise à jour de l'historique des thèmes
            if main_theme and main_theme != 'inconnu':
                self.theme_history.add(main_theme)
            
            # Mise à jour des termes utilisés
            key_terms = self._extract_key_terms(content)
            self.used_terms.update(dict(key_terms))
            
            # Enregistrement du contenu
            entry = {
                'id': content_id,
                'theme': main_theme,
                'sous_themes': sub_themes,
                'date_creation': datetime.now().isoformat(),
                'content_preview': content[:200] + '...'
            }
            self.content_registry.append(entry)
            
            logger.info(f"Base de connaissances mise à jour avec le contenu ID: {content_id}")
            return content_id
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour de la base de connaissances: {str(e)}", exc_info=True)
            raise

    def _create_analysis_report(self, analysis_result: Dict[str, Any]) -> ThemeAnalysis:
        """
        Crée un rapport d'analyse structuré à partir des résultats bruts.
        
        Args:
            analysis_result: Résultats bruts de l'analyse
            
        Returns:
            ThemeAnalysis: Rapport d'analyse structuré
        """
        try:
            # Extraction des informations principales
            theme_principal = analysis_result.get('theme_principal', {})
            sous_themes = analysis_result.get('sous_themes', [])
            repetitions = analysis_result.get('repetitions', [])
            recommandations = analysis_result.get('recommandations', [])
            
            # Création du rapport
            report = ThemeAnalysis(
                main_theme=theme_principal.get('nom', 'Inconnu'),
                sub_themes=[st.get('nom', '') for st in sous_themes if isinstance(st, dict) and st.get('nom')],
                repetitions={rep.get('terme'): rep.get('occurrences') for rep in repetitions if isinstance(rep, dict) and rep.get('terme')},
                recommendations=recommandations,
                content_gaps=analysis_result.get('lacunes', [])
            )
            
            # Ajout des répétitions si présentes
            if 'repetitions' in analysis_result:
                report.repetitions = {
                    rep.get('terme', ''): rep.get('occurrences', 0)
                    for rep in analysis_result['repetitions']
                    if rep.get('terme')
                }
            
            # Ajout des liens thématiques
            if 'liens_thematiques' in analysis_result:
                report.related_content = [
                    {
                        'type': lt.get('type', ''),
                        'titre': lt.get('titre', ''),
                        'lien': lt.get('lien', '')
                    }
                    for lt in analysis_result['liens_thematiques']
                    if lt.get('titre')
                ]
            
            # Plan de progression
            if 'plan_progression' in analysis_result:
                report.publication_schedule = {
                    'etapes': analysis_result['plan_progression'].get('etapes_suivantes', []),
                    'themes': analysis_result['plan_progression'].get('themes_complementaires', []),
                    'calendrier': analysis_result['plan_progression'].get('calendrier_suggere', '')
                }
            
            return report
            
        except Exception as e:
            logger.error(f"Erreur lors de la création du rapport d'analyse: {str(e)}")
            return ThemeAnalysis(
                main_theme="Erreur",
                recommendations=["Une erreur est survenue lors de la création du rapport d'analyse"]
            )
        
        # Ajout des termes (sauf ceux marqués comme surutilisés)
        if 'termes_surutilises' in analysis_result:
            for item in analysis_result['termes_surutilises']:
                self.used_terms.discard(item['terme'].lower())
                for alt in item.get('alternatives', []):
                    self.used_terms.add(alt.lower())
    
    def get_theme_analysis(self, theme: str) -> Dict[str, Any]:
        """
        Récupère l'analyse complète pour un thème donné.
        
        Args:
            theme: Thème à analyser
            
        Returns:
            Dict: Analyse complète du thème avec statistiques et recommandations
        """
        try:
            # Recherche du thème dans l'historique
            theme_lower = theme.lower()
            theme_frequency = sum(1 for t in self.theme_history if t.lower() == theme_lower)
            
            # Recherche des contenus liés à ce thème
            related_contents = []
            for content in self.content_registry:
                content_theme = content.get('theme', '').lower()
                if theme_lower in content_theme or theme_lower in content.get('content_preview', '').lower():
                    related_contents.append(content)
            
            # Construction de l'analyse
            return {
                "theme": theme,
                "frequence": theme_frequency,
                "premiere_occurrence": min(
                    [c.get('timestamp', '') for c in related_contents],
                    default="Inconnue"
                ),
                "derniere_occurrence": max(
                    [c.get('timestamp', '') for c in related_contents],
                    default="Inconnue"
                ) if related_contents else "Inconnue",
                "contenus_lies": [
                    {
                        "id": c.get('id', ''),
                        "type": c.get('type', 'inconnu'),
                        "date": c.get('timestamp', ''),
                        "apercu": c.get('content_preview', '')
                    }
                    for c in related_contents[:5]  # Limite à 5 contenus
                ],
                "recommandations": [
                    f"Approfondir le thème avec un contenu de type 'guide' ou 'étude de cas'"
                    if theme_frequency < 3 else
                    f"Éviter la redondance, ce thème a déjà été traité {theme_frequency} fois"
                ]
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse du thème {theme}: {str(e)}")
            return {"error": f"Erreur lors de l'analyse du thème: {str(e)}"}
    
    def get_theme_suggestions(self, current_theme: str) -> List[str]:
        """
        Suggère des thèmes similaires mais non encore utilisés.
        
        Args:
            current_theme: Thème actuel pour lequel générer des suggestions
            
        Returns:
            List[str]: Liste des suggestions de thèmes
        """
        theme_lower = current_theme.lower()
        suggestions = []
        
        # Mapping des thèmes vers des suggestions
        theme_mapping = {
            "phytothérapie": ["plantes médicinales", "herbes chinoises", "décoctions"],
            "diététique": ["énergétique des aliments", "nutrition en MTC", "régimes thérapeutiques"],
            "qi gong": ["exercices énergétiques", "mouvements thérapeutiques", "respiration"]
        }
        
        # Trouver des suggestions basées sur le thème actuel
        for key, values in theme_mapping.items():
            if key in theme_lower:
                suggestions.extend([v for v in values if v not in self.theme_history])
        
        return suggestions[:5]  # Limite à 5 suggestions
    
    def get_content_registry(self) -> List[Dict[str, Any]]:
        """
        Récupère le registre complet des contenus analysés.
        
        Returns:
            List[Dict]: Liste des entrées de contenu avec leurs métadonnées
        """
        return self.content_registry
    
    def get_content_by_id(self, content_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupère un contenu spécifique par son ID.
        
        Args:
            content_id: ID du contenu à récupérer
            
        Returns:
            Optional[Dict]: L'entrée de contenu si trouvée, None sinon
        """
        for entry in self.content_registry:
            if entry.get('id') == content_id:
                return entry
        return None
