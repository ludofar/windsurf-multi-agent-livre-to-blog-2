from .base_agent import BaseAgent
from typing import Dict, Any, List, Tuple, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import json
import logging
import os
import re
from datetime import datetime

logger = logging.getLogger(__name__)

class ContentType(str, Enum):
    ARTICLE = "article_blog"
    SOCIAL_MEDIA = "reseau_social"
    NEWSLETTER = "newsletter"
    GUIDE = "guide_pratique"
    VIDEO = "video"

class ValidationStatus(str, Enum):
    APPROVED = "approuve"
    NEEDS_REVISION = "revise"
    REJECTED = "rejette"

@dataclass
class ValidationResult:
    """Résultat détaillé de la validation du contenu."""
    status: ValidationStatus
    score: float = 0.0
    issues: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

class ValidatorAgent(BaseAgent):
    """
    Agent responsable de la validation de la qualité et de l'éthique du contenu MTC.
    
    Responsabilités :
    1. Validation de l'exactitude des informations MTC
    2. Vérification de la conformité éthique
    3. Contrôle de la qualité rédactionnelle
    4. Vérification de la conformité réglementaire
    """
    
    def __init__(self, model: str = None):
        default_model = os.getenv('DEFAULT_MODEL', 'qwen/qwen3-coder')
        super().__init__(
            name="MTC Content Validator",
            model=model or default_model
        )
        
    async def generate_prompt(self, *args, **kwargs) -> str:
        """
        Génère un prompt pour le modèle de langage.
        
        Args:
            *args: Arguments positionnels
            **kwargs: Arguments nommés
            
        Returns:
            str: Le prompt formaté pour le modèle de langage
        """
        # Cette méthode est une implémentation de la méthode abstraite de BaseAgent
        # Elle est principalement utilisée par les méthodes internes de validation
        # qui génèrent leurs propres prompts spécifiques
        
        # Si un prompt est fourni directement dans les arguments, on le retourne
        if 'prompt' in kwargs:
            return kwargs['prompt']
            
        # Sinon, on utilise le prompt par défaut pour la validation
        content = kwargs.get('content', '')
        content_type = kwargs.get('content_type', ContentType.ARTICLE)
        
        return f"""
        Vous êtes un validateur expert en contenu MTC. Analysez le contenu suivant et fournissez une évaluation détaillée.
        
        Type de contenu: {content_type}
        
        Contenu à valider:
        {content}
        
        Fournissez une analyse complète incluant:
        1. Qualité rédactionnelle
        2. Exactitude des informations MTC
        3. Conformité éthique
        4. Suggestions d'amélioration
        """
        
        # Critères de validation
        self.validation_criteria = [
            "exactitude_mtc",
            "ethique_et_responsabilite",
            "qualite_redactionnelle",
            "structure_et_clarte",
            "conformite_reglementaire",
            "optimisation_seo"
        ]
        
        # Termes et concepts sensibles en MTC
        self.sensitive_terms = {
            "traite": ["guérir", "soigner", "traitement"],
            "diagnostique": ["diagnostic", "maladie", "pathologie"],
            "therapeutique": ["thérapie", "remède", "médicament"]
        }
        
        # Sources fiables de référence
        self.trusted_sources = [
            "OMS", "HAS", "OMS MTC", "Collèges de MTC", "Textes classiques"
        ]
        
        # Historique des validations
        self.validation_history: List[Dict[str, Any]] = []
    
    async def validate_content(
        self, 
        content: str, 
        content_type: ContentType = ContentType.ARTICLE,
        target_audience: str = "grand public"
    ) -> ValidationResult:
        """
        Valide un contenu selon les critères de qualité et d'éthique MTC.
        
        Args:
            content: Contenu à valider
            content_type: Type de contenu (article, post, etc.)
            target_audience: Public cible (grand public, professionnels, etc.)
            
        Returns:
            ValidationResult: Résultat détaillé de la validation
        """
        try:
            # Extraire le contenu textuel si un dictionnaire est fourni
            text_content = content.get('content', content) if isinstance(content, dict) else content

            # Vérifications préliminaires
            if not isinstance(text_content, str) or not text_content.strip():
                return ValidationResult(
                    status=ValidationStatus.REJECTED,
                    issues=[{"type": "empty_content", "message": "Le contenu est vide"}]
                )
            
            # Vérification des termes sensibles
            sensitive_issues = self._check_sensitive_terms(content)
            
            # Génération du prompt de validation
            prompt = self._generate_validation_prompt(content, content_type, target_audience)
            
            # Appel au modèle
            response = await self.call_model(prompt)
            
            # Traitement de la réponse
            if not response or 'error' in response:
                logger.error("Erreur lors de l'appel au modèle de validation")
                return self._fallback_validation(content)
                
            # Analyse de la réponse
            validation_data = self._parse_validation_response(response)
            
            # Vérification des aspects critiques
            critical_issues = self._check_critical_issues(content, validation_data)
            critical_issues.extend(sensitive_issues)
            
            # Calcul du score global
            score = self._calculate_global_score(validation_data)
            
            # Détermination du statut
            status = self._determine_validation_status(score, critical_issues)
            
            # Création du rapport
            result = ValidationResult(
                status=status,
                score=score,
                issues=critical_issues,
                metadata={
                    "content_type": content_type,
                    "validation_date": datetime.now().isoformat(),
                    "model_used": self.model
                }
            )
            
            # Enregistrement de la validation
            self._log_validation(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur lors de la validation du contenu: {str(e)}", exc_info=True)
            return ValidationResult(
                status=ValidationStatus.NEEDS_REVISION,
                issues=[{"type": "validation_error", "message": str(e)}]
            )
    
    def _generate_validation_prompt(
        self, 
        content: str, 
        content_type: ContentType,
        target_audience: str
    ) -> str:
        """Génère le prompt pour la validation du contenu MTC."""
        return f"""
        Tu es un expert en validation de contenu pour la Médecine Traditionnelle Chinoise (MTC).
        
        TÂCHE :
        Valide rigoureusement le contenu suivant selon les critères stricts de qualité, d'exactitude
        et d'éthique de la MTC.
        
        CONTEXTE :
        - Type de contenu : {content_type.value}
        - Public cible : {target_audience}
        - Date actuelle : {datetime.now().strftime('%d/%m/%Y')}
        
        CONTENU À VALIDER :
        {content[:8000]}{'... [contenu tronqué]' if len(content) > 8000 else ''}
        
        CRITÈRES DE VALIDATION :
        1. EXACTITUDE MTC :
           - Les concepts MTC sont-ils correctement expliqués ?
           - Les termes techniques sont-ils précis et appropriés ?
           - Les références aux textes classiques sont-elles exactes ?
           
        2. ÉTHIQUE ET RESPONSABILITÉ :
           - Y a-t-il des allégations thérapeutiques non fondées ?
           - Les mises en garde nécessaires sont-elles présentes ?
           - Le contenu respecte-t-il la déontologie médicale ?
           
        3. QUALITÉ RÉDACTIONNELLE :
           - Le contenu est-il clair et compréhensible ?
           - Le ton est-il adapté au public cible ?
           - La structure est-elle logique et cohérente ?
           
        4. CONFORMITÉ RÉGLEMENTAIRE :
           - Respect des mentions légales et des droits d'auteur
           - Conformité aux réglementations en vigueur
           - Sources et références correctement citées
        
        FORMAT DE SORTIE (JSON) :
        {{
            "evaluation_globale": {{
                "score": 1-5,
                "niveau_acceptation": "approuve | revise | rejette",
                "synthese": "Résumé concis de l'évaluation"
            }},
            "evaluations_detaillees": [
                {{
                    "categorie": "exactitude_mtc | ethique | qualite | conformite",
                    "note": 1-5,
                    "commentaire": "Analyse détaillée",
                    "elements_a_corriger": ["élément 1", "élément 2"],
                    "suggestions": ["suggestion 1", "suggestion 2"]
                }}
            ],
            "problemes_critiques": [
                {{
                    "type": "ethique | exactitude | conformite",
                    "gravite": "mineur | majeur | critique",
                    "description": "Description du problème",
                    "localisation": "Section concernée",
                    "correction": "Proposition de correction"
                }}
            ],
            "verification_sources": [
                {{
                    "affirmation": "Affirmation à vérifier",
                    "statut": "verifie | a_verifier | conteste",
                    "commentaire": "Commentaire sur la vérification",
                    "sources": ["source 1", "source 2"]
                }}
            ]
        }}
        """
        
    def _parse_validation_response(self, response: str) -> Dict[str, Any]:
        """
        Parse et valide la réponse du modèle de validation.
        
        Args:
            response: Réponse brute du modèle
            
        Returns:
            Dict: Données structurées de validation
        """
        try:
            # Extraction du JSON
            start = response.find('{')
            end = response.rfind('}') + 1
            if start == -1 or end == 0:
                raise ValueError("Aucun JSON valide trouvé dans la réponse")
                
            json_str = response[start:end]
            data = json.loads(json_str)
            
            # Validation de la structure de base
            required_sections = ['evaluation_globale', 'evaluations_detaillees']
            for section in required_sections:
                if section not in data:
                    raise ValueError(f"Section requise manquante: {section}")
            
            return data
            
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Erreur lors du parsing de la réponse: {str(e)}")
            return {"error": f"Erreur lors de l'analyse de la réponse: {str(e)}"}
    
    def _check_sensitive_terms(self, content: str) -> List[Dict[str, str]]:
        """
        Vérifie la présence de termes sensibles dans le contenu.
        
        Args:
            content: Contenu à analyser
            
        Returns:
            List[Dict]: Liste des problèmes détectés
        """
        issues = []
        content_lower = content.lower()
        
        for category, terms in self.sensitive_terms.items():
            for term in terms:
                if term in content_lower:
                    issues.append({
                        'type': 'terme_sensible',
                        'categorie': category,
                        'terme': term,
                        'message': f"Terme sensible détecté: '{term}'"
                    })
        
        return issues
    
    def _check_critical_issues(
        self, 
        content: str, 
        validation_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Vérifie les problèmes critiques dans le contenu.
        
        Args:
            content: Contenu analysé
            validation_data: Données de validation du modèle
            
        Returns:
            List[Dict]: Liste des problèmes critiques
        """
        critical_issues = []
        
        # Vérification des problèmes critiques signalés par le modèle
        for issue in validation_data.get('problemes_critiques', []):
            if issue.get('gravite') in ['majeur', 'critique']:
                critical_issues.append({
                    'type': 'critique_modele',
                    'gravite': issue.get('gravite'),
                    'description': issue.get('description', 'Problème critique non détaillé'),
                    'localisation': issue.get('localisation', 'Non spécifiée'),
                    'correction': issue.get('correction', 'Aucune correction proposée')
                })
        
        # Vérification des affirmations contestées
        for fact in validation_data.get('verification_sources', []):
            if fact.get('statut') == 'conteste':
                critical_issues.append({
                    'type': 'affirmation_controversee',
                    'gravite': 'majeur',
                    'description': f"Affirmation controversée: {fact.get('affirmation', 'Non spécifiée')}",
                    'commentaire': fact.get('commentaire', 'Aucun commentaire'),
                    'sources': fact.get('sources', [])
                })
        
        return critical_issues
    
    def _calculate_global_score(self, validation_data: Dict[str, Any]) -> float:
        """
        Calcule le score global de validation.
        
        Args:
            validation_data: Données de validation du modèle
            
        Returns:
            float: Score global (0-5)
        """
        if 'evaluation_globale' in validation_data:
            return validation_data['evaluation_globale'].get('score', 0.0)
        
        # Calcul à partir des évaluations détaillées si le score global n'est pas fourni
        evaluations = validation_data.get('evaluations_detaillees', [])
        if not evaluations:
            return 0.0
            
        total = sum(eval_.get('note', 0) for eval_ in evaluations)
        return round(total / len(evaluations), 1)
    
    def _determine_validation_status(
        self, 
        score: float, 
        critical_issues: List[Dict[str, Any]]
    ) -> ValidationStatus:
        """
        Détermine le statut de validation en fonction du score et des problèmes critiques.
        
        Args:
            score: Score global de validation
            critical_issues: Liste des problèmes critiques
            
        Returns:
            ValidationStatus: Statut de validation
        """
        # Rejet immédiat en cas de problème critique
        if any(issue.get('gravite') == 'critique' for issue in critical_issues):
            return ValidationStatus.REJECTED
            
        # Décision basée sur le score
        if score >= 4.0:
            return ValidationStatus.APPROVED
        elif score >= 2.5:
            return ValidationStatus.NEEDS_REVISION
        else:
            return ValidationStatus.REJECTED
    
    def _fallback_validation(self, content: str) -> ValidationResult:
        """
        Effectue une validation de secours en cas d'échec de la validation principale.
        
        Args:
            content: Contenu à valider
            
        Returns:
            ValidationResult: Résultat de validation de secours
        """
        # Vérifications de base
        issues = self._check_sensitive_terms(content)
        
        # Analyse simple du contenu
        word_count = len(content.split())
        has_references = bool(re.search(r'\[\d+\]|\([A-Za-z]+,? \d{4}\)', content))
        
        # Création du résultat
        result = ValidationResult(
            status=ValidationStatus.NEEDS_REVISION,
            score=2.0,
            issues=issues,
            warnings=["Validation de secours effectuée en raison d'une erreur du système"],
            metadata={
                "word_count": word_count,
                "has_references": has_references,
                "fallback_used": True
            }
        )
        
        # Ajout d'avertissements supplémentaires
        if word_count < 100:
            result.warnings.append("Le contenu semble très court pour une validation précise")
        if not has_references:
            result.warnings.append("Aucune référence détectée dans le contenu")
            
        return result
    
    def _log_validation(self, result: ValidationResult) -> None:
        """
        Enregistre les résultats de la validation dans l'historique.
        
        Args:
            result: Résultat de la validation à enregistrer
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "status": result.status.value,
            "score": result.score,
            "issue_count": len(result.issues),
            "metadata": result.metadata
        }
        
        self.validation_history.append(log_entry)
        
        # Limite la taille de l'historique
        if len(self.validation_history) > 100:
            self.validation_history.pop(0)
            
        logger.info(f"Validation terminée - Statut: {result.status.value}, Score: {result.score}")
    
    def generate_validation_report(self, result: ValidationResult) -> str:
        """
        Génère un rapport de validation lisible à partir d'un résultat de validation.
        
        Args:
            result: Résultat de validation à formater
            
        Returns:
            str: Rapport de validation formaté
        """
        report = []
        
        # En-tête du rapport
        report.append(
            f"=== RAPPORT DE VALIDATION MTC ===\n"
            f"Date : {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
            f"Statut : {result.status.value.upper()}\n"
            f"Score : {result.score:.1f}/5.0\n"
            f"Type de contenu : {result.metadata.get('content_type', 'Non spécifié')}\n"
        )
        
        # Avertissements
        if result.warnings:
            report.append("\n=== AVERTISSEMENTS ===")
            for warning in result.warnings:
                report.append(f"⚠️ {warning}")
        
        # Problèmes critiques
        if result.issues:
            report.append("\n=== PROBLÈMES IDENTIFIÉS ===")
            for i, issue in enumerate(result.issues, 1):
                report.append(
                    f"\n**Problème #{i}**\n"
                    f"Type : {issue.get('type', 'Non spécifié')}\n"
                    f"Gravité : {issue.get('gravite', 'Non spécifiée')}\n"
                    f"Description : {issue.get('description', 'Aucune description')}\n"
                    f"Localisation : {issue.get('localisation', 'Non spécifiée')}"
                )
                
                if 'correction' in issue:
                    report.append(f"Correction suggérée : {issue['correction']}")
                
                if 'sources' in issue and issue['sources']:
                    report.append("Sources : " + ", ".join(issue['sources']))
        
        # Détails des évaluations si disponibles
        if 'evaluations' in result.metadata:
            report.append("\n=== DÉTAILS DES ÉVALUATIONS ===")
            for eval_ in result.metadata['evaluations']:
                report.append(
                    f"\n**{eval_.get('categorie', 'Catégorie inconnue').upper()}** : "
                    f"{eval_.get('note', 0)}/5\n"
                    f"{eval_.get('commentaire', 'Aucun commentaire')}"
                )
                
                if 'elements_a_corriger' in eval_ and eval_['elements_a_corriger']:
                    report.append("\nÉléments à corriger :")
                    for elem in eval_['elements_a_corriger'][:5]:  # Limite à 5 éléments
                        report.append(f"- {elem}")
                    
                    if len(eval_['elements_a_corriger']) > 5:
                        report.append(f"... et {len(eval_['elements_a_corriger']) - 5} autres")
                
                if 'suggestions' in eval_ and eval_['suggestions']:
                    report.append("\nSuggestions d'amélioration :")
                    for suggestion in eval_['suggestions'][:3]:  # Limite à 3 suggestions
                        report.append(f"- {suggestion}")
        
        # Vérification des sources si disponible
        if 'verification_sources' in result.metadata and result.metadata['verification_sources']:
            report.append("\n=== VÉRIFICATION DES SOURCES ===")
            for i, source in enumerate(result.metadata['verification_sources'], 1):
                status_emoji = {
                    'verifie': '✅',
                    'a_verifier': '❓',
                    'conteste': '❌'
                }.get(source.get('statut', '').lower(), '❔')
                
                report.append(
                    f"\n**Source #{i}** {status_emoji}\n"
                    f"Affirmation : {source.get('affirmation', 'Non spécifiée')}\n"
                    f"Statut : {source.get('statut', 'inconnu').capitalize()}\n"
                    f"Commentaire : {source.get('commentaire', 'Aucun commentaire')}"
                )
                
                if 'sources' in source and source['sources']:
                    report.append("Références : " + "; ".join(source['sources']))
        
        # Recommandations finales
        if result.suggestions:
            report.append("\n=== RECOMMANDATIONS ===")
            for i, suggestion in enumerate(result.suggestions, 1):
                report.append(f"{i}. {suggestion}")
        
        # Pied de page
        report.append(
            f"\n=== FIN DU RAPPORT ===\n"
            f"Validation effectuée par : {self.name}\n"
            f"Modèle utilisé : {self.model}"
        )
        
        return "\n".join(report)
    
    async def validate_content_with_report(
        self,
        content: str,
        content_type: ContentType = ContentType.ARTICLE,
        target_audience: str = "grand public",
        detailed: bool = True
    ) -> Dict[str, Any]:
        """
        Valide un contenu et génère un rapport détaillé en une seule étape.
        
        Args:
            content: Contenu à valider
            content_type: Type de contenu (article, post, etc.)
            target_audience: Public cible (grand public, professionnels, etc.)
            detailed: Si True, inclut les détails complets dans le rapport
            
        Returns:
            Dict: Résultat de la validation avec rapport formaté
        """
        # Validation du contenu
        validation_result = await self.validate_content(
            content=content,
            content_type=content_type,
            target_audience=target_audience
        )
        
        # Génération du rapport
        report = self.generate_validation_report(validation_result)
        
        # Préparation du résultat
        result = {
            'status': validation_result.status.value,
            'score': validation_result.score,
            'issues': validation_result.issues,
            'warnings': validation_result.warnings,
            'report': report,
            'metadata': validation_result.metadata
        }
        
        # Ajout des détails si demandé
        if detailed:
            result.update({
                'evaluations': validation_result.metadata.get('evaluations', []),
                'sources_verification': validation_result.metadata.get('verification_sources', [])
            })
        
        return result
