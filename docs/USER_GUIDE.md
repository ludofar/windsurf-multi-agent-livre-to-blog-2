# 📘 Guide Utilisateur - Système Multi-Agent MTC

> **Dernière mise à jour** : 06/08/2025  
> **Version** : 1.0.0

## 📋 Table des Matières

1. [Présentation](#-présentation)
2. [Installation](#-installation)
3. [Configuration](#-configuration)
4. [Utilisation de Base](#-utilisation-de-base)
5. [Agents et Fonctionnalités](#-agents-et-fonctionnalités)
6. [Workflows](#-workflows)
7. [Dépannage](#-dépannage)
8. [FAQ](#-faq)

## 🌟 Présentation

Bienvenue dans le système multi-agent pour la génération de contenu sur la Médecine Traditionnelle Chinoise (MTC). Ce guide vous accompagne dans la prise en main de l'outil.

### À qui s'adresse ce guide ?
- Rédacteurs de contenu
- Éditeurs web
- Professionnels de la MTC
- Gestionnaires de communauté

### Fonctionnalités clés
- Analyse de livres PDF sur la MTC
- Génération d'articles de blog
- Création de publications sociales
- Production de visuels adaptés
- Validation automatique du contenu

## 🚀 Installation

### Prérequis
- Python 3.8 ou supérieur
- Compte OpenRouter avec crédits
- Git (recommandé)

### Étapes d'installation

1. **Cloner le dépôt**
   ```bash
   git clone [URL_DU_DEPOT]
   cd windsurf-multi-agent-livre-to-blog
   ```

2. **Créer un environnement virtuel**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Sur Windows : venv\Scripts\activate
   ```

3. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurer les variables d'environnement**
   ```bash
   cp .env.example .env
   # Éditer le fichier .env avec vos informations
   ```

## ⚙️ Configuration

### Fichier .env
```ini
# Clé API OpenRouter
OPENROUTER_API_KEY=votre_cle_api

# Modèle par défaut (Qwen recommandé)
DEFAULT_MODEL=qwen/qwen-72b-chat

# Paramètres du modèle
TEMPERATURE=0.7
MAX_TOKENS=2048

# Chemins des dossiers
INPUT_DIR=./input
OUTPUT_DIR=./output
```

### Structure des dossiers
```
.
├── input/           # Fichiers PDF à analyser
├── output/          # Contenu généré
│   ├── content/     # Articles et publications
│   ├── reports/     # Rapports d'analyse
│   └── visuals/     # Fichiers visuels
└── logs/            # Journaux d'exécution
```

## 🖥 Utilisation de Base

### Lancer une analyse complète
```bash
python daily_workflow.py --input mon_livre.pdf
```

### Options de ligne de commande
```
--input       Chemin vers le fichier PDF à analyser
--output      Dossier de sortie (défaut: ./output)
--model       Modèle à utiliser (défaut: qwen/qwen-72b-chat)
--batch       Traitement par lots de plusieurs fichiers
--verbose     Mode verbeux pour le débogage
```

## 🤖 Agents et Fonctionnalités

### 1. Analyseur PDF
**Rôle** : Extrait et structure le contenu des livres PDF

**Utilisation** :
```python
from agents.pdf_analyzer import PDFAnalyzerAgent

analyzer = PDFAnalyzerAgent()
results = await analyzer.analyze_pdf("chemin/vers/mon_livre.pdf")
```

### 2. Stratège de Contenu
**Rôle** : Planifie la stratégie éditoriale

**Fonctionnalités** :
- Calendrier de publication
- Stratégie SEO
- Ciblage du public

### 3. Rédacteur d'Articles
**Rôle** : Rédige des articles complets

**Format de sortie** :
- Markdown
- Balises SEO
- Structure optimisée

### 4. Créateur de Contenu Social
**Rôle** : Génère des publications pour Facebook

**Fonctionnalités** :
- 2 publications quotidiennes
- Hashtags pertinents
- Appels à l'action

### 5. Créateur de Visuels
**Rôle** : Génère des descriptions pour les visuels

**Spécifications** :
- Format d'image
- Style visuel
- Éléments graphiques

### 6. Validateur
**Rôle** : Vérifie la qualité du contenu

**Vérifications** :
- Exactitude médicale
- Cohérence thématique
- Qualité rédactionnelle

## 🔄 Workflows

### Workflow Quotidien Automatisé

Le workflow quotidien est le point d'entrée principal pour générer du contenu à partir de vos documents sources. Il gère automatiquement tout le processus de bout en bout.

#### Fonctionnalités clés
- Traitement parallèle des documents (jusqu'à 3 fichiers en même temps)
- Génération de contenu structuré en Markdown
- Création de rapports détaillés
- Gestion robuste des erreurs
- Journalisation complète

#### Comment l'utiliser

1. **Préparation**
   - Placez vos fichiers PDF ou TXT dans le dossier `input/`
   - Vérifiez que votre fichier `.env` est correctement configuré

2. **Exécution**
   ```bash
   python daily_workflow.py
   ```
   
   Options disponibles :
   ```bash
   # Pour traiter plus de fichiers en parallèle (par défaut: 3)
   python daily_workflow.py --max-concurrent 5
   ```

3. **Résultats**
   - Contenu généré : `output/content/[nom-du-fichier]/`
     - `article_blog.md` : Article complet au format Markdown
     - `metadata.json` : Métadonnées structurées
     - `social_posts/` : Publications pour les réseaux sociaux
     - `visuals/` : Descriptions pour la création de visuels
   
   - Rapports : `output/reports/`
     - `rapport_YYYY-MM-DD.json` : Données brutes du rapport
     - `rapport_YYYY-MM-DD.md` : Version lisible du rapport

4. **Surveillance**
   - Consultez les logs dans la console pour suivre la progression
   - Les erreurs sont enregistrées dans les fichiers de log et incluses dans le rapport

#### Format du rapport quotidien

Le rapport quotidien inclut :
- Statistiques de production (fichiers traités, articles générés, etc.)
- Liste des contenus générés avec métadonnées
- Détails des erreurs rencontrées
- Points d'amélioration
- Plan pour le jour suivant

#### Bonnes pratiques
- Vérifiez toujours le rapport de fin d'exécution
- Consultez les logs en cas d'erreur
- Conservez une trace des rapports pour suivre l'évolution de la production

### Workflow Standard
1. Déposer un PDF dans le dossier `input/`
2. Lancer le script principal
3. Récupérer les résultats dans `output/`

### Workflow Avancé
1. Préparer un fichier de configuration JSON
2. Lancer le traitement par lots
3. Analyser les rapports générés

## 🛠 Dépannage

### Problèmes courants

#### 1. Erreur d'API
```
Erreur : Clé API invalide
```
**Solution** : Vérifiez votre clé API dans le fichier .env

#### 2. Problème de mémoire
```
Erreur : Mémoire insuffisante
```
**Solution** :
- Réduisez la taille des lots
- Utilisez un modèle plus petit
- Augmentez la mémoire disponible

#### 3. Fichier PDF corrompu
```
Erreur : Impossible de lire le fichier PDF
```
**Solution** :
- Vérifiez l'intégrité du fichier
- Convertissez le PDF en texte si nécessaire

## ❓ FAQ

### Puis-je utiliser d'autres modèles que Qwen ?
Oui, tout modèle supporté par OpenRouter est compatible. Modifiez simplement la variable `DEFAULT_MODEL` dans le fichier .env.

### Comment ajouter de nouveaux modèles de contenu ?
Créez une nouvelle classe dans le dossier `templates/` et mettez à jour la configuration de l'agent concerné.

### Le système prend-il en charge d'autres langues ?
Oui, bien que principalement conçu pour le français, le système peut être adapté à d'autres langues en modifiant les modèles et les paramètres de langue.

### Comment contribuer au projet ?
1. Forkez le dépôt
2. Créez une branche pour votre fonctionnalité
3. Soumettez une pull request

## 📞 Support

Pour toute question ou problème, veuillez ouvrir une issue sur notre [dépôt GitHub](https://github.com/votre-utilisateur/windsurf-multi-agent-livre-to-blog/issues).

---

*Ce document est fourni tel quel, sans garantie d'aucune sorte. Dernière mise à jour : Août 2025.*
