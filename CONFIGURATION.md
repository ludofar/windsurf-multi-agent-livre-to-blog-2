# Configuration du Projet

Ce document explique comment configurer l'environnement pour exécuter le projet de conversion de livres en articles de blog.

## Prérequis

- Python 3.9 ou supérieur
- pip (gestionnaire de paquets Python)
- Un compte OpenRouter avec des crédits disponibles

## Installation des dépendances

1. Créez un environnement virtuel (recommandé) :
   ```bash
   python -m venv venv
   source venv/bin/activate  # Sur Windows : .\venv\Scripts\activate
   ```

2. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

## Configuration des clés API

1. Créez un fichier `.env` à la racine du projet :
   ```bash
   cp .env.example .env
   ```

2. Modifiez le fichier `.env` avec vos clés API :
   ```env
   # Clé API OpenRouter (obtenue sur https://openrouter.ai/keys)
   OPENROUTER_API_KEY=votre_cle_api_ici
   
   # Configuration du cache (en secondes, 86400 = 24h)
   CACHE_TTL=86400
   
   # Niveau de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
   LOG_LEVEL=INFO
   
   # Modèle par défaut à utiliser
   DEFAULT_MODEL=qwen/qwen3-coder
   ```

## Variables d'environnement

| Variable | Description | Valeur par défaut |
|----------|-------------|-------------------|
| `OPENROUTER_API_KEY` | Clé API pour OpenRouter | Requise |
| `CACHE_TTL` | Durée de vie du cache en secondes | 86400 (24h) |
| `LOG_LEVEL` | Niveau de journalisation | INFO |
| `DEFAULT_MODEL` | Modèle de langage par défaut | qwen/qwen3-coder |

## Configuration des agents

### PDFAnalyzerAgent
- Extrait le texte des fichiers PDF
- Analyse la structure du document
- Détecte les chapitres et sections

### BlogWriterAgent
- Génère des articles de blog à partir du contenu analysé
- Crée des titres accrocheurs
- Structure le contenu de manière optimale

### OptimizerAgent
- Optimise les prompts pour réduire les coûts
- Analyse les performances
- Ajuste les paramètres des appels API

## Démarrer l'application

1. Activez l'environnement virtuel si ce n'est pas déjà fait :
   ```bash
   source venv/bin/activate  # Sur Windows : .\venv\Scripts\activate
   ```

2. Lancez l'application :
   ```bash
   python -m uvicorn app.main:app --reload
   ```

3. L'application sera disponible à l'adresse :
   ```
   http://127.0.0.1:8000
   ```

## Dépannage

### Erreurs d'authentification
- Vérifiez que votre clé API OpenRouter est correcte
- Assurez-vous d'avoir des crédits disponibles sur votre compte

### Problèmes de dépendances
- Si vous rencontrez des erreurs d'importation, essayez de réinstaller les dépendances :
  ```bash
  pip install -r requirements.txt --force-reinstall
  ```

### Problèmes de performance
- Réduisez la taille des lots de traitement
- Augmentez les délais entre les appels API
- Vérifiez l'utilisation de la mémoire

## Support

Pour toute question ou problème, veuillez ouvrir une issue sur le dépôt du projet.
