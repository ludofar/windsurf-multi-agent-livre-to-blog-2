# 🌿 Système Multi-Agent pour la Génération de Contenu MTC

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Un système intelligent de génération de contenu sur la Médecine Traditionnelle Chinoise (MTC) utilisant une architecture multi-agents pour transformer des livres PDF en contenu numérique optimisé.

## 🌟 Fonctionnalités Principales

### 🔍 Analyse Avancée
- Extraction intelligente du contenu des livres PDF
- Identification des concepts clés et de leurs relations
- Détection des thèmes récurrents et des sujets sous-représentés

### ✍️ Création de Contenu
- Articles de blog détaillés (1500-2000 mots)
- Publications sociales optimisées pour Facebook
- Suggestions de titres accrocheurs et de méta-descriptions

### 🎨 Gestion des Visuels
- Génération de prompts détaillés pour la création de visuels
- Métadonnées bilingues (français/anglais) pour chaque visuel
- Spécifications techniques précises pour les visuels générés

### ✅ Validation Automatisée
- Vérification de la qualité rédactionnelle
- Contrôle de la cohérence thématique
- Validation éthique et réglementaire du contenu
- Gestion des erreurs et journalisation détaillée
- Rapports quotidiens automatisés

## 🏗 Architecture du Système

Le système repose sur une architecture modulaire composée de 7 agents spécialisés :

| Agent | Rôle | Technologies Clés |
|-------|------|-------------------|
| **PDF Analyzer** | Extraction et analyse du contenu | PyPDF, NLP, Qwen |
| **Theme Manager** | Gestion de la cohérence thématique | Vecteurs sémantiques |
| **Content Strategy** | Planification éditoriale | Analyse de tendances |
| **Blog Writer** | Rédaction d'articles | Modèles de langage avancés |
| **Social Creator** | Génération de posts | Templates adaptatifs |
| **Visual Creator** | Génération de prompts pour visuels | Modèles de langage avancés |
| **Validator** | Assurance qualité | Règles métier, NLP |

## 🚀 Mise en Route

### Prérequis

- Python 3.8 ou supérieur
- Compte [OpenRouter](https://openrouter.ai/) avec crédits
- Variables d'environnement configurées (voir `.env.example`)

### Installation

1. **Cloner le dépôt**
   ```bash
   git clone https://github.com/votre-utilisateur/windsurf-multi-agent-mtc.git
   cd windsurf-multi-agent-mtc
   ```

2. **Configurer l'environnement virtuel**
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate
   
   # Linux/MacOS
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurer les variables d'environnement**
   ```bash
   cp .env.example .env
   # Éditer le fichier .env avec vos clés API
   ```

## 🛠 Utilisation

### Workflow Quotidien Automatisé

Le script `daily_workflow.py` gère le processus complet :

```bash
python daily_workflow.py
```

### Structure des Dossiers

```
.
├── input/               # PDFs à traiter
├── output/
│   ├── content/        # Contenu généré
│   └── reports/        # Rapports quotidiens
├── agents/             # Code source des agents
├── .env.example        # Modèle de configuration
└── requirements.txt    # Dépendances
```

## 📊 Métriques de Performance

Le système génère des rapports quotidiens incluant :
- Nombre de PDF traités
- Articles générés
- Publications créées
- Taux de validation
- Temps de traitement

## 🤝 Contribution

Les contributions sont les bienvenues ! Voici comment contribuer :

1. Forkez le projet
2. Créez une branche (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Poussez vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## 📝 Licence

Distribué sous licence MIT. Voir `LICENSE` pour plus d'informations.

## 📧 Contact

Votre Nom - [@votretwitter](https://twitter.com/votretwitter) - email@example.com

Lien du projet : [https://github.com/votre-utilisateur/windsurf-multi-agent-mtc](https://github.com/votre-utilisateur/windsurf-multi-agent-mtc)

4. Configurer les variables d'environnement :
   ```bash
   cp .env.example .env
   # Éditer le fichier .env avec vos clés API
   ```

## 🔧 Configuration

Créer un fichier `.env` à la racine du projet avec :

```
OPENROUTER_API_KEY=votre_cle_api_openrouter
DEFAULT_MODEL=qwen/qwen-72b-chat  # Modèle Qwen par défaut
```

## 🏃‍♂️ Utilisation

1. Placer vos fichiers PDF dans le dossier `input/`
2. Exécuter le script principal :
   ```bash
   python main.py --input input/votre_livre.pdf
   ```

## 📂 Structure du Projet

```
.
├── agents/                 # Modules des agents
│   ├── __init__.py
│   ├── base_agent.py      # Classe de base pour tous les agents
│   ├── pdf_analyzer.py    # Agent d'analyse PDF
│   ├── content_strategy.py # Stratégie de contenu
│   ├── blog_writer.py     # Rédaction d'articles
│   ├── social_creator.py  # Création de contenu social
│   ├── visual_creator.py  # Génération de visuels
│   ├── theme_manager.py   # Gestion de la cohérence
│   └── validator.py       # Validation du contenu
├── config/                # Fichiers de configuration
├── input/                 # Fichiers PDF d'entrée
├── output/                # Contenu généré
│   ├── blog/              # Articles de blog
│   ├── social/            # Publications sociales
│   └── assets/            # Visuels générés
├── utils/                 # Utilitaires
├── main.py                # Point d'entrée
├── requirements.txt       # Dépendances
└── README.md              # Ce fichier
```

## 🤖 Modèles Utilisés

- **Modèle par défaut** : Qwen via OpenRouter
- **Autres modèles** : Peuvent être configurés via le fichier `.env`

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🙏 Remerciements

- [OpenRouter](https://openrouter.ai/) pour l'accès aux modèles de langage
- L'équipe Qwen pour leurs modèles de pointe
