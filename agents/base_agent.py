from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union
import os
import json
import aiohttp
import asyncio
import logging
import random
import time
from pathlib import Path
from enum import Enum, auto
from typing import Dict, Any, Optional, Type, Tuple
from dataclasses import dataclass
from dotenv import load_dotenv

# Ajout des imports pour les utilitaires
import sys
sys.path.append(str(Path(__file__).parent.parent))
from utils.cache_manager import cache_manager
from utils.metrics import metrics, measure_execution_time


class ErrorType(Enum):
    """Types d'erreurs possibles"""
    NETWORK = auto()        # Problème de connexion
    RATE_LIMIT = auto()     # Trop de requêtes
    TIMEOUT = auto()        # Délai d'attente dépassé
    INVALID_INPUT = auto()  # Données d'entrée invalides
    MODEL_ERROR = auto()    # Erreur côté modèle
    VALIDATION = auto()     # Échec de validation
    UNKNOWN = auto()        # Erreur non catégorisée


@dataclass
class APIError(Exception):
    """Classe d'erreur personnalisée pour les erreurs d'API"""
    error_type: ErrorType
    message: str
    status_code: Optional[int] = None
    retry_after: Optional[int] = None
    original_exception: Optional[Exception] = None
    
    def __str__(self):
        return f"{self.error_type.name}: {self.message} (status: {self.status_code})"

# Chargement des variables d'environnement
load_dotenv()

# Configuration du logging
logging.basicConfig(level=os.getenv('LOG_LEVEL', 'INFO'))
logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    def __init__(self, name: str, model: str = None, use_cache: bool = True, cache_ttl: int = 86400):
        """
        Initialise un nouvel agent.
        
        Args:
            name: Nom de l'agent
            model: Modèle à utiliser (par défaut: valeur de la variable d'environnement DEFAULT_MODEL ou 'qwen/qwen3-coder')
            use_cache: Active ou désactive le cache pour cet agent
            cache_ttl: Durée de vie du cache en secondes (par défaut: 24h)
        """
        self.name = name
        self.model = model or os.getenv('DEFAULT_MODEL', 'qwen/qwen3-coder')
        self.memory = {}
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        self.base_url = "https://openrouter.ai/api/v1"
        self.use_cache = use_cache
        self.cache_ttl = cache_ttl
        
        # Initialisation des compteurs de métriques
        self.metrics_prefix = f"agent.{self.name.lower().replace(' ', '_')}"
        self._init_metrics()
        
        if not self.api_key:
            metrics.counter(
                f"{self.metrics_prefix}.errors",
                f"Erreurs de l'agent {self.name}",
                error_type="missing_api_key"
            ).inc()
            raise ValueError("La clé API OpenRouter est requise. Veuillez la définir dans le fichier .env")
            
        logger.info(f"Initialisation de l'agent {name} (modèle: {self.model}, cache: {'activé' if use_cache else 'désactivé'})")
        
    def _init_metrics(self):
        """Initialise les compteurs de métriques pour cet agent"""
        # Compteurs d'appels
        metrics.counter(
            f"{self.metrics_prefix}.calls",
            f"Nombre total d'appels à l'agent {self.name}"
        )
        
        # Compteurs d'erreurs
        metrics.counter(
            f"{self.metrics_prefix}.errors",
            f"Nombre total d'erreurs pour l'agent {self.name}"
        )
        
        # Métriques de performance
        metrics.histogram(
            f"{self.metrics_prefix}.processing_time",
            f"Temps de traitement pour l'agent {self.name} (secondes)",
            buckets=[0.1, 0.5, 1, 2, 5, 10, 30, 60]
        )
        
        # Métriques de cache
        metrics.counter(
            f"{self.metrics_prefix}.cache",
            f"Utilisation du cache pour l'agent {self.name}",
            type="hit"
        )
        metrics.counter(
            f"{self.metrics_prefix}.cache",
            f"Utilisation du cache pour l'agent {self.name}",
            type="miss"
        )
    
    def _classify_error(self, error: Exception) -> Tuple[ErrorType, str, Optional[int]]:
        """
        Classe une exception et retourne son type, un message et un délai de réessai.
        
        Args:
            error: L'exception à classifier
            
        Returns:
            Tuple (type_erreur, message, delai_reexecution)
        """
        # Gestion des erreurs réseau
        if isinstance(error, asyncio.TimeoutError):
            return ErrorType.TIMEOUT, "Délai d'attente dépassé", 5
            
        if isinstance(error, aiohttp.ClientError):
            if "timed out" in str(error).lower():
                return ErrorType.TIMEOUT, "Délai d'attente réseau dépassé", 10
            return ErrorType.NETWORK, f"Erreur réseau: {str(error)}", 5
            
        # Gestion des erreurs d'API
        if hasattr(error, 'status_code'):
            status_code = getattr(error, 'status_code')
            
            # Erreurs 4xx
            if status_code == 400:
                return ErrorType.INVALID_INPUT, "Requête invalide", None
            elif status_code == 401:
                return ErrorType.VALIDATION, "Clé API invalide", None
            elif status_code == 403:
                return ErrorType.VALIDATION, "Accès refusé", None
            elif status_code == 404:
                return ErrorType.INVALID_INPUT, "Ressource non trouvée", None
            elif status_code == 429:  # Rate limiting
                retry_after = int(getattr(error, 'response', {}).headers.get('Retry-After', 5))
                return ErrorType.RATE_LIMIT, "Limite de débit atteinte", retry_after
                
            # Erreurs 5xx
            elif status_code >= 500:
                return ErrorType.MODEL_ERROR, f"Erreur serveur (HTTP {status_code})", 30
                
        # Erreurs de validation
        if isinstance(error, json.JSONDecodeError):
            return ErrorType.VALIDATION, "Réponse JSON invalide", 2
            
        # Par défaut, on considère que c'est une erreur inconnue
        return ErrorType.UNKNOWN, f"Erreur inattendue: {str(error)}", 5
        
    @abstractmethod
    def generate_prompt(self, input_data: Dict[str, Any]) -> str:
        """Génère le prompt spécifique pour l'agent"""
        pass
    
    def _get_cache_key(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Génère une clé de cache basée sur les données d'entrée et la configuration de l'agent.
        
        Args:
            input_data: Données d'entrée pour le traitement
            
        Returns:
            Un dictionnaire contenant les informations pour la clé de cache
        """
        return {
            'agent_name': self.name,
            'model': self.model,
            'input_data': input_data,
            'version': '1.0'  # Version du cache (incrémenter en cas de changement de format)
        }
    
    @measure_execution_time
    async def _call_model_api(self, prompt: str, max_retries: int = 3) -> str:
        """
        Appelle l'API du modèle avec gestion des erreurs et backoff exponentiel.
        
        Args:
            prompt: Le prompt à envoyer au modèle
            max_retries: Nombre maximum de tentatives
            
        Returns:
            La réponse brute du modèle
            
        Raises:
            APIError: En cas d'échec après plusieurs tentatives
        """
        base_delay = 1  # Délai initial en secondes
        attempt = 0
        last_error = None
        
        # Enregistrer la tentative d'appel API
        metrics.counter(
            f"{self.metrics_prefix}.api.calls",
            f"Nombre d'appels API pour l'agent {self.name}",
            model=self.model
        ).inc()
        
        # Mesurer la taille du prompt
        prompt_tokens = len(prompt) // 4  # Estimation grossière des tokens
        metrics.histogram(
            f"{self.metrics_prefix}.prompt_tokens",
            f"Taille des prompts pour l'agent {self.name} (tokens estimés)",
            model=self.model
        ).observe(prompt_tokens)
        
        while attempt < max_retries:
            attempt += 1
            
            try:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "HTTP-Referer": "https://github.com/your-repo",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": int(os.getenv('MAX_TOKENS', 4000)),
                    "temperature": float(os.getenv('TEMPERATURE', 0.7)),
                    "top_p": float(os.getenv('TOP_P', 0.9))
                }
                
                timeout = aiohttp.ClientTimeout(total=60)  # Timeout de 60 secondes
                
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    start_time = time.time()
                    async with session.post(
                        f"{self.base_url}/chat/completions",
                        headers=headers,
                        json=payload
                    ) as response:
                        response_time = time.time() - start_time
                        
                        # Enregistrer le temps de réponse
                        metrics.histogram(
                            f"{self.metrics_prefix}.api.response_time",
                            f"Temps de réponse de l'API pour l'agent {self.name}",
                            model=self.model,
                            status_code=response.status
                        ).observe(response_time)
                        
                        # Traitement de la réponse
                        if response.status == 200:
                            response_data = await response.json()
                            
                            # Enregistrer les métriques de réponse réussie
                            if 'usage' in response_data:
                                usage = response_data['usage']
                                metrics.histogram(
                                    f"{self.metrics_prefix}.api.tokens.prompt",
                                    f"Tokens d'entrée utilisés par l'agent {self.name}",
                                    model=self.model
                                ).observe(usage.get('prompt_tokens', 0))
                                
                                metrics.histogram(
                                    f"{self.metrics_prefix}.api.tokens.completion",
                                    f"Tokens de sortie utilisés par l'agent {self.name}",
                                    model=self.model
                                ).observe(usage.get('completion_tokens', 0))
                                
                                metrics.histogram(
                                    f"{self.metrics_prefix}.api.tokens.total",
                                    f"Total des tokens utilisés par l'agent {self.name}",
                                    model=self.model
                                ).observe(usage.get('total_tokens', 0))
                            
                            return response_data['choices'][0]['message']['content']
                            
                        # Gestion des erreurs HTTP
                        error_text = await response.text()
                        logger.error(f"Erreur API (tentative {attempt}/{max_retries}): "
                                   f"HTTP {response.status} - {error_text}")
                        
                        # Enregistrer l'erreur dans les métriques
                        metrics.counter(
                            f"{self.metrics_prefix}.api.errors",
                            f"Erreurs d'API pour l'agent {self.name}",
                            status_code=response.status,
                            attempt=attempt,
                            max_retries=max_retries
                        ).inc()
                        
                        # Création d'une exception avec le statut HTTP
                        error = Exception(f"HTTP {response.status}: {error_text}")
                        error.status_code = response.status
                        error.response = response
                        raise error
                        
            except Exception as e:
                # Classification de l'erreur
                error_type, error_msg, retry_after = self._classify_error(e)
                last_error = APIError(
                    error_type=error_type,
                    message=error_msg,
                    status_code=getattr(e, 'status_code', None),
                    retry_after=retry_after,
                    original_exception=e
                )
                
                # Journalisation détaillée
                logger.warning(
                    f"Tentative {attempt}/{max_retries} échouée pour {self.name}: "
                    f"{error_type.name} - {error_msg}"
                )
                
                # Si c'est la dernière tentative ou si l'erreur ne nécessite pas de réessai
                if attempt >= max_retries or not retry_after:
                    logger.error(
                        f"Échec après {attempt} tentatives pour {self.name}. "
                        f"Dernière erreur: {str(last_error)}"
                    )
                    raise last_error
                
                # Calcul du délai avec backoff exponentiel et jitter
                delay = min(
                    base_delay * (2 ** (attempt - 1)) + random.uniform(0, 1),
                    60  # Maximum 60 secondes
                )
                
                # Utiliser le délai Retry-After si disponible (pour le rate limiting)
                wait_time = retry_after if retry_after > delay else delay
                
                logger.info(f"Nouvelle tentative dans {wait_time:.1f} secondes...")
                await asyncio.sleep(wait_time)
        
        # Ne devrait jamais arriver ici à cause des raises précédents
        raise last_error or APIError(
            error_type=ErrorType.UNKNOWN,
            message="Échec inconnu lors de l'appel à l'API"
        )
    
    @measure_execution_time
    async def process(self, input_data: Dict[str, Any], use_cache: Optional[bool] = None) -> Dict[str, Any]:
        """
        Traite l'entrée et retourne la sortie de l'agent via l'API OpenRouter.
        
        Args:
            input_data: Dictionnaire contenant les données d'entrée
            use_cache: Si True, utilise le cache (par défaut: valeur de l'instance)
            
        Returns:
            Dictionnaire contenant la réponse de l'agent
            
        Raises:
            APIError: En cas d'erreur lors du traitement
        """
        # Enregistrer le début du traitement
        start_time = time.time()
        metrics.counter(
            f"{self.metrics_prefix}.calls",
            f"Nombre total d'appels à l'agent {self.name}"
        ).inc()
        
        # Utiliser la valeur de l'instance si use_cache n'est pas spécifié
        use_cache = self.use_cache if use_cache is None else use_cache
        cache_key = None
        
        try:
            # Vérifier si on peut utiliser le cache
            if use_cache:
                try:
                    cache_key = self._get_cache_key(input_data)
                    cached_response = await cache_manager.get(cache_key)
                    if cached_response is not None:
                        logger.debug(f"Réponse trouvée dans le cache pour l'agent {self.name}")
                        
                        # Enregistrer un hit de cache
                        metrics.counter(
                            f"{self.metrics_prefix}.cache",
                            f"Utilisation du cache pour l'agent {self.name}",
                            type="hit"
                        ).inc()
                        
                        # Enregistrer le temps total de traitement (avec cache)
                        metrics.histogram(
                            f"{self.metrics_prefix}.processing_time",
                            f"Temps de traitement pour l'agent {self.name} (secondes)",
                            cache="hit"
                        ).observe(time.time() - start_time)
                        
                        return cached_response
                        
                    # Enregistrer un miss de cache
                    metrics.counter(
                        f"{self.metrics_prefix}.cache",
                        f"Utilisation du cache pour l'agent {self.name}",
                        type="miss"
                    ).inc()
                    
                except Exception as e:
                    logger.warning(f"Erreur lors de l'accès au cache pour {self.name}: {str(e)}")
            
            # Générer le prompt
            try:
                prompt = self.generate_prompt(input_data)
                if not prompt or not isinstance(prompt, str):
                    raise ValueError("Le prompt généré est vide ou n'est pas une chaîne de caractères")
            except Exception as e:
                logger.error(f"Échec de la génération du prompt pour {self.name}: {str(e)}")
                raise APIError(
                    error_type=ErrorType.INVALID_INPUT,
                    message=f"Échec de la génération du prompt: {str(e)}",
                    original_exception=e
                )
            
            # Appeler l'API du modèle avec gestion des erreurs
            logger.info(f"Appel à l'API du modèle pour l'agent {self.name}")
            content = await self._call_model_api(prompt)
            
            # Parser la réponse
            result = self._parse_response(content)
            if not isinstance(result, dict):
                raise ValueError("La réponse parsée doit être un dictionnaire")
                
            # Mettre en cache le résultat si nécessaire
            if use_cache and cache_key and result is not None:
                try:
                    logger.debug(f"Mise en cache du résultat pour l'agent {self.name}")
                    await cache_manager.set(cache_key, result, ttl=self.cache_ttl)
                except Exception as e:
                    logger.warning(f"Échec de la mise en cache pour {self.name}: {str(e)}")
            
            # Enregistrer le temps total de traitement (sans cache)
            metrics.histogram(
                f"{self.metrics_prefix}.processing_time",
                f"Temps de traitement pour l'agent {self.name} (secondes)",
                cache="miss"
            ).observe(time.time() - start_time)
            
            return result
            
        except Exception as e:
            # Enregistrer l'erreur dans les métriques
            error_type = e.__class__.__name__
            metrics.counter(
                f"{self.metrics_prefix}.errors",
                f"Erreurs pour l'agent {self.name}",
                error_type=error_type
            ).inc()
            
            # Enregistrer le temps de traitement même en cas d'erreur
            metrics.histogram(
                f"{self.metrics_prefix}.processing_time",
                f"Temps de traitement pour l'agent {self.name} (secondes)",
                error=error_type,
                cache="error"
            ).observe(time.time() - start_time)
            
            # Relancer l'exception pour une gestion ultérieure
            if isinstance(e, APIError):
                raise e
            else:
                raise APIError(
                    error_type=ErrorType.UNKNOWN,
                    message=f"Erreur inattendue lors du traitement par {self.name}: {str(e)}",
                    original_exception=e
                )
            
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse la réponse du modèle en un format structuré"""
        # À implémenter par les classes filles si nécessaire
        return {"response": response}
