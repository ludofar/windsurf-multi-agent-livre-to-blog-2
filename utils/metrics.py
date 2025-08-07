"""
Module de gestion des métriques de performance.
Permet de collecter et d'exporter des métriques sur les performances du système.
"""
import time
import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any
from enum import Enum
import logging
import json
import os
from pathlib import Path

logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Types de métriques supportés"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"

@dataclass
class Metric:
    """Classe de base pour les métriques"""
    name: str
    type: MetricType
    description: str = ""
    labels: Dict[str, str] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

@dataclass
class Counter(Metric):
    """Compteur pour suivre le nombre d'occurrences d'un événement"""
    value: int = 0
    type: MetricType = field(default=MetricType.COUNTER, init=False)

    def inc(self, value: int = 1) -> None:
        """Incrémente le compteur"""
        self.value += value
        self.timestamp = time.time()

@dataclass
class Gauge(Metric):
    """Jauge pour mesurer une valeur à un instant donné"""
    value: float = 0.0
    type: MetricType = field(default=MetricType.GAUGE, init=False)

    def set(self, value: float) -> None:
        """Définit la valeur de la jauge"""
        self.value = value
        self.timestamp = time.time()

    def inc(self, value: float = 1.0) -> None:
        """Incrémente la jauge"""
        self.value += value
        self.timestamp = time.time()

    def dec(self, value: float = 1.0) -> None:
        """Décrémente la jauge"""
        self.value -= value
        self.timestamp = time.time()

@dataclass
class Histogram(Metric):
    """Histogramme pour suivre la distribution des valeurs"""
    buckets: Dict[float, int] = field(default_factory=dict)
    sum_value: float = 0.0
    count: int = 0
    type: MetricType = field(default=MetricType.HISTOGRAM, init=False)

    def observe(self, value: float) -> None:
        """Ajoute une observation à l'histogramme"""
        self.sum_value += value
        self.count += 1
        self.timestamp = time.time()
        
        # Arrondir la valeur pour regrouper dans des buckets
        bucket = round(value, 2)
        self.buckets[bucket] = self.buckets.get(bucket, 0) + 1

class MetricsCollector:
    """Collecteur de métriques"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MetricsCollector, cls).__new__(cls)
            cls._instance._metrics: Dict[str, Metric] = {}
            cls._instance._exporters: List[Callable[[Dict[str, Any]], None]] = []
        return cls._instance
    
    def register_exporter(self, exporter: Callable[[Dict[str, Any]], None]) -> None:
        """Enregistre un exporteur de métriques"""
        self._exporters.append(exporter)
    
    def counter(self, name: str, description: str = "", **labels) -> Counter:
        """Crée ou récupère un compteur"""
        key = self._get_metric_key(name, labels)
        if key not in self._metrics:
            self._metrics[key] = Counter(name=name, description=description, labels=labels)
        return self._metrics[key]
    
    def gauge(self, name: str, description: str = "", **labels) -> Gauge:
        """Crée ou récupère une jauge"""
        key = self._get_metric_key(name, labels)
        if key not in self._metrics:
            self._metrics[key] = Gauge(name=name, description=description, labels=labels)
        return self._metrics[key]
    
    def histogram(self, name: str, description: str = "", **labels) -> Histogram:
        """Crée ou récupère un histogramme"""
        key = self._get_metric_key(name, labels)
        if key not in self._metrics:
            self._metrics[key] = Histogram(name=name, description=description, labels=labels)
        return self._metrics[key]
    
    def get_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Retourne toutes les métriques au format dictionnaire"""
        metrics = {}
        for key, metric in self._metrics.items():
            metrics[key] = {
                'name': metric.name,
                'type': metric.type.value,
                'description': metric.description,
                'labels': metric.labels,
                'timestamp': metric.timestamp,
                'value': getattr(metric, 'value', None),
                'buckets': getattr(metric, 'buckets', None),
                'sum': getattr(metric, 'sum_value', None),
                'count': getattr(metric, 'count', None)
            }
        return metrics
    
    async def export_metrics(self) -> None:
        """Exporte les métriques via tous les exporteurs enregistrés"""
        metrics_data = self.get_metrics()
        for exporter in self._exporters:
            try:
                if asyncio.iscoroutinefunction(exporter):
                    await exporter(metrics_data)
                else:
                    exporter(metrics_data)
            except Exception as e:
                logger.error(f"Erreur lors de l'export des métriques: {str(e)}")
    
    def _get_metric_key(self, name: str, labels: Dict[str, str]) -> str:
        """Génère une clé unique pour une métrique basée sur son nom et ses labels"""
        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{name}{{{label_str}}}" if label_str else name

def setup_metrics_export(export_interval: int = 60, export_dir: str = "metrics") -> None:
    """Configure l'export périodique des métriques dans des fichiers JSON"""
    os.makedirs(export_dir, exist_ok=True)
    
    def json_exporter(metrics_data: Dict[str, Any]) -> None:
        """Exporte les métriques dans un fichier JSON"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = Path(export_dir) / f"metrics_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'metrics': metrics_data
                }, f, indent=2, ensure_ascii=False)
            logger.debug(f"Métriques exportées vers {filename}")
        except Exception as e:
            logger.error(f"Erreur lors de l'export des métriques: {str(e)}")
    
    # Enregistrer l'exportateur
    collector = MetricsCollector()
    collector.register_exporter(json_exporter)
    
    # Planifier l'export périodique
    async def periodic_export():
        while True:
            await asyncio.sleep(export_interval)
            await collector.export_metrics()
    
    # Démarrer la tâche d'export en arrière-plan
    asyncio.create_task(periodic_export())
    logger.info(f"Export des métriques configuré toutes les {export_interval} secondes")

# Créer une instance globale du collecteur de métriques
metrics = MetricsCollector()

# Décorateur pour mesurer le temps d'exécution des fonctions
def measure_execution_time(func):
    """Décorateur pour mesurer le temps d'exécution d'une fonction"""
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            duration = time.time() - start_time
            
            # Enregistrer la métrique
            metric_name = f"{func.__module__}.{func.__name__}.duration"
            metrics.histogram(metric_name, f"Temps d'exécution de {func.__name__}", 
                            module=func.__module__).observe(duration)
            
            # Incrémenter le compteur de succès
            metrics.counter(f"{func.__module__}.{func.__name__}.calls",
                          f"Nombre d'appels à {func.__name__}",
                          status="success").inc()
            
            return result
        except Exception as e:
            # En cas d'erreur, enregistrer la métrique d'erreur
            duration = time.time() - start_time
            metric_name = f"{func.__module__}.{func.__name__}.duration"
            metrics.histogram(metric_name, f"Temps d'exécution de {func.__name__}", 
                            module=func.__module__).observe(duration)
            
            # Incrémenter le compteur d'erreurs
            metrics.counter(f"{func.__module__}.{func.__name__}.calls",
                          f"Nombre d'appels à {func.__name__}",
                          status="error",
                          error_type=e.__class__.__name__).inc()
            raise
    
    def sync_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            
            # Enregistrer la métrique
            metric_name = f"{func.__module__}.{func.__name__}.duration"
            metrics.histogram(metric_name, f"Temps d'exécution de {func.__name__}", 
                            module=func.__module__).observe(duration)
            
            # Incrémenter le compteur de succès
            metrics.counter(f"{func.__module__}.{func.__name__}.calls",
                          f"Nombre d'appels à {func.__name__}",
                          status="success").inc()
            
            return result
        except Exception as e:
            # En cas d'erreur, enregistrer la métrique d'erreur
            duration = time.time() - start_time
            metric_name = f"{func.__module__}.{func.__name__}.duration"
            metrics.histogram(metric_name, f"Temps d'exécution de {func.__name__}", 
                            module=func.__module__).observe(duration)
            
            # Incrémenter le compteur d'erreurs
            metrics.counter(f"{func.__module__}.{func.__name__}.calls",
                          f"Nombre d'appels à {func.__name__}",
                          status="error",
                          error_type=e.__class__.__name__).inc()
            raise
    
    return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
