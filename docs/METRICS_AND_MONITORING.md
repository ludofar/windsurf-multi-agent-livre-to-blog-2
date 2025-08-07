# Métriques et Monitoring

Ce document explique comment utiliser le système de métriques et de monitoring intégré au système multi-agents.

## Vue d'ensemble

Le système de métriques permet de collecter et d'exporter des données de performance et d'utilisation des agents. Ces métriques sont essentielles pour :

- Surveiller les performances du système
- Détecter les goulots d'étranglement
- Comprendre l'utilisation des ressources
- Dépanner les problèmes
- Optimiser les coûts

## Types de métriques collectées

### Métriques de workflow

- **Exécution du workflow**
  - `workflow.duration` : Durée totale d'exécution
  - `workflow.files_processed` : Nombre de fichiers traités
  - `workflow.articles_generated` : Nombre d'articles générés
  - `workflow.errors` : Nombre d'erreurs rencontrées

### Métriques d'agent

Pour chaque agent, les métriques suivantes sont collectées :

- **Appels** : Nombre total d'appels à l'agent
  - `agent.{nom_agent}.calls`

- **Temps de traitement** : Distribution des temps de réponse
  - `agent.{nom_agent}.processing_time`
  - Tags : `cache` (hit/miss/error)

- **Cache** : Utilisation du cache
  - `agent.{nom_agent}.cache` (type="hit" ou "miss")

### Métriques de contenu

- **Qualité du contenu**
  - `content.article.length` : Longueur des articles générés
  - `content.article.generation_time` : Temps de génération moyen
  - `content.social_posts.generated` : Nombre de publications générées
  - `content.visuals.generated` : Nombre de visuels générés

- **Erreurs** : Nombre et types d'erreurs
  - `agent.{nom_agent}.errors`
  - Tags : `error_type`

### Métriques d'API

Pour chaque appel à l'API du modèle :

- **Appels API** : Nombre total d'appels
  - `agent.{nom_agent}.api.calls`

- **Temps de réponse** : Temps de réponse de l'API
  - `agent.{nom_agent}.api.response_time`
  - Tags : `status_code`, `model`

- **Utilisation des tokens** : Nombre de tokens utilisés
  - `agent.{nom_agent}.api.tokens.prompt`
  - `agent.{nom_agent}.api.tokens.completion`
  - `agent.{nom_agent}.api.tokens.total`

- **Erreurs API** : Erreurs lors des appels API
  - `agent.{nom_agent}.api.errors`
  - Tags : `status_code`, `attempt`, `max_retries`

## Utilisation

### Accès aux métriques

Les métriques sont accessibles via l'instance `metrics` :

```python
from utils.metrics import metrics

# Obtenir toutes les métriques
all_metrics = metrics.get_metrics()

# Exporter les métriques (appelle tous les exportateurs enregistrés)
await metrics.export_metrics()
```

### Export des métriques

Par défaut, les métriques sont exportées dans des fichiers JSON dans le répertoire `metrics/` toutes les 60 secondes.

Pour configurer l'export :

```python
from utils.metrics import setup_metrics_export

# Configurer l'export des métriques (par défaut : toutes les 60s dans ./metrics)
setup_metrics_export(export_interval=60, export_dir="metrics")
```

### Ajout d'exportateurs personnalisés

Vous pouvez ajouter vos propres exportateurs (par exemple, pour envoyer les métriques à Prometheus, Datadog, etc.) :

```python
async def custom_exporter(metrics_data):
    # Traiter les métriques (envoyer à une base de données, un service externe, etc.)
    print(f"Exporting {len(metrics_data)} metrics")

# Enregistrer l'exportateur
metrics.register_exporter(custom_exporter)
```

### Décoration des fonctions

Pour mesurer automatiquement le temps d'exécution d'une fonction et compter les appels/réussites/échecs :

```python
from utils.metrics import measure_execution_time

@measure_execution_time
async def ma_fonction_importante():
    # Code de la fonction
    pass
```

## Exemple de sortie JSON

Voici un exemple de ce à quoi ressemblent les métriques exportées :

```json
{
  "timestamp": "2025-02-15T14:30:45.123456",
  "metrics": {
    "agent.pdf_analyzer.calls": {
      "name": "agent.pdf_analyzer.calls",
      "type": "counter",
      "description": "Nombre total d'appels à l'agent PDF Analyzer",
      "value": 42,
      "timestamp": 1708007445.123456
    },
    "agent.pdf_analyzer.processing_time": {
      "name": "agent.pdf_analyzer.processing_time",
      "type": "histogram",
      "description": "Temps de traitement pour l'agent PDF Analyzer (secondes)",
      "buckets": {
        "0.1": 10,
        "0.5": 25,
        "1.0": 5,
        "2.0": 2
      },
      "sum": 25.7,
      "count": 42,
      "timestamp": 1708007445.123456
    }
  }
}
```

## Bonnes pratiques

1. **Étiquetage** : Utilisez des tags pertinents pour faciliter le filtrage et l'agrégation des métriques.

2. **Granularité** : Ne collectez que les métriques dont vous avez besoin pour éviter la surcharge.

3. **Export régulier** : Exportez régulièrement les métriques pour éviter la perte de données en cas de plantage.

4. **Surveillance proactive** : Configurez des alertes basées sur les métriques pour détecter rapidement les problèmes.

5. **Rétention** : Définissez une politique de rétention pour les données de métriques afin de gérer l'espace disque.

## Dépannage

### Les métriques ne s'affichent pas

- Vérifiez que `setup_metrics_export()` a été appelé au démarrage de l'application.
- Vérifiez les permissions d'écriture dans le répertoire d'export.
- Vérifiez les logs pour les erreurs potentielles.

### Performances dégradées

- Réduisez la fréquence d'export si nécessaire.
- Vérifiez que les exportateurs personnalisés ne sont pas trop gourmands en ressources.
- Envisagez d'utiliser un système de métriques dédié pour les charges importantes.

## Intégration avec des outils externes

### Prometheus

Pour exposer les métriques au format Prometheus :

```python
from prometheus_client import start_http_server, Counter, Histogram

# Créer des métriques Prometheus
calls = Counter('agent_calls_total', 'Number of agent calls', ['agent_name'])
processing_time = Histogram('agent_processing_time_seconds', 'Agent processing time', ['agent_name'])

# Mettre à jour les métriques dans l'exportateur
def prometheus_exporter(metrics_data):
    for metric_name, metric in metrics_data.items():
        if metric_name.endswith('.calls'):
            agent = metric_name.split('.')[1]
            calls.labels(agent_name=agent).inc(metric['value'])
        # ... autres métriques

# Démarrer le serveur Prometheus
start_http_server(8000)
```

### Grafana

Importez les fichiers JSON générés dans Grafana ou utilisez un connecteur Prometheus pour visualiser les métriques en temps réel.
