"""
Gestionnaire de cache pour les réponses des modèles.

Ce module fournit une implémentation simple d'un cache en mémoire avec expiration
et persistance sur disque.
"""
import json
import hashlib
import time
from pathlib import Path
from typing import Any, Dict, Optional
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class CacheManager:
    """Gestionnaire de cache pour les réponses des modèles."""
    
    def __init__(self, cache_dir: str = "cache", ttl: int = 86400, max_size: int = 1000):
        """
        Initialise le gestionnaire de cache.
        
        Args:
            cache_dir: Répertoire pour le stockage persistant du cache
            ttl: Durée de vie des entrées en secondes (24h par défaut)
            max_size: Nombre maximum d'entrées en cache
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = ttl
        self.max_size = max_size
        self.memory_cache: Dict[str, Dict] = {}
        self._load_from_disk()
    
    def _get_cache_key(self, input_data: Dict) -> str:
        """Génère une clé de cache unique à partir des données d'entrée."""
        # Création d'une représentation en chaîne des données d'entrée
        input_str = json.dumps(input_data, sort_keys=True)
        # Génération d'un hachage MD5 de la chaîne
        return hashlib.md5(input_str.encode('utf-8')).hexdigest()
    
    def _get_cache_file_path(self, cache_key: str) -> Path:
        """Retourne le chemin du fichier de cache pour une clé donnée."""
        return self.cache_dir / f"{cache_key}.json"
    
    def _load_from_disk(self):
        """Charge le cache depuis le disque."""
        try:
            for cache_file in self.cache_dir.glob("*.json"):
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        entry = json.load(f)
                        # Vérification de l'expiration
                        if entry.get('expires_at', 0) > time.time():
                            self.memory_cache[cache_file.stem] = entry
                        else:
                            cache_file.unlink()  # Supprime les entrées expirées
                except (json.JSONDecodeError, KeyError) as e:
                    logger.warning(f"Cache corrompu {cache_file}: {e}")
                    cache_file.unlink()
            logger.info(f"Cache chargé avec {len(self.memory_cache)} entrées valides")
        except Exception as e:
            logger.error(f"Erreur lors du chargement du cache: {e}")
    
    def _save_to_disk(self, cache_key: str, data: Dict):
        """Sauvegarde une entrée sur le disque."""
        try:
            cache_file = self._get_cache_file_path(cache_key)
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde du cache: {e}")
    
    def _cleanup(self):
        """Nettoie le cache si nécessaire."""
        if len(self.memory_cache) > self.max_size:
            # Trier les entrées par date d'expiration (les plus anciennes d'abord)
            sorted_entries = sorted(
                self.memory_cache.items(),
                key=lambda x: x[1].get('expires_at', 0)
            )
            # Supprimer les entrées excédentaires (les plus anciennes)
            for key, _ in sorted_entries[:len(self.memory_cache) - self.max_size]:
                cache_file = self._get_cache_file_path(key)
                if cache_file.exists():
                    cache_file.unlink()
                self.memory_cache.pop(key, None)
    
    async def get(self, input_data: Dict) -> Optional[Dict]:
        """
        Récupère une entrée du cache.
        
        Args:
            input_data: Données d'entrée utilisées pour générer la clé de cache
            
        Returns:
            Les données en cache ou None si non trouvées ou expirées
        """
        cache_key = self._get_cache_key(input_data)
        
        # Vérification en mémoire d'abord
        if cache_key in self.memory_cache:
            entry = self.memory_cache[cache_key]
            if entry.get('expires_at', 0) > time.time():
                logger.debug(f"Cache hit pour la clé: {cache_key}")
                return entry.get('data')
            else:
                # Suppression si expiré
                self.memory_cache.pop(cache_key, None)
                cache_file = self._get_cache_file_path(cache_key)
                if cache_file.exists():
                    cache_file.unlink()
        
        # Vérification sur disque (au cas où le cache mémoire aurait été vidé)
        cache_file = self._get_cache_file_path(cache_key)
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    entry = json.load(f)
                    if entry.get('expires_at', 0) > time.time():
                        # Mise en cache en mémoire pour les accès futurs
                        self.memory_cache[cache_key] = entry
                        return entry.get('data')
                    else:
                        # Suppression si expiré
                        cache_file.unlink()
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Cache corrompu {cache_file}: {e}")
                cache_file.unlink()
        
        return None
    
    async def set(self, input_data: Dict, result: Any, ttl: Optional[int] = None):
        """
        Ajoute une entrée dans le cache.
        
        Args:
            input_data: Données d'entrée utilisées pour générer la clé de cache
            result: Données à mettre en cache
            ttl: Durée de vie en secondes (utilise la valeur par défaut si None)
        """
        if result is None:
            return
            
        cache_key = self._get_cache_key(input_data)
        ttl = ttl or self.ttl
        expires_at = time.time() + ttl
        
        entry = {
            'data': result,
            'created_at': datetime.now().isoformat(),
            'expires_at': expires_at,
            'ttl': ttl
        }
        
        # Mise à jour du cache mémoire
        self.memory_cache[cache_key] = entry
        
        # Sauvegarde sur disque
        self._save_to_disk(cache_key, entry)
        
        # Nettoyage si nécessaire
        if len(self.memory_cache) > self.max_size * 1.1:  # Nettoyer si on dépasse de 10%
            self._cleanup()
        
        logger.debug(f"Entrée mise en cache avec la clé: {cache_key}")
    
    def clear(self, expired_only: bool = False):
        """
        Vide le cache.
        
        Args:
            expired_only: Si True, ne supprime que les entrées expirées
        """
        current_time = time.time()
        keys_to_remove = []
        
        # Identification des clés à supprimer
        for key, entry in self.memory_cache.items():
            if not expired_only or entry.get('expires_at', 0) <= current_time:
                keys_to_remove.append(key)
        
        # Suppression des entrées
        for key in keys_to_remove:
            cache_file = self._get_cache_file_path(key)
            if cache_file.exists():
                cache_file.unlink()
            self.memory_cache.pop(key, None)
        
        logger.info(f"Cache vidé: {len(keys_to_remove)} entrées supprimées")

# Instance globale pour une utilisation facile
cache_manager = CacheManager()
