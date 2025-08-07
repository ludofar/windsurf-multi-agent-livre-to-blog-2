# 📚 Documentation des Agents

Ce document fournit une documentation complète de tous les agents du système multi-agent MTC.

## 📋 Table des Matières

1. [Agent de Base](#-agent-de-base)
2. [Analyseur PDF](#-analyseur-pdf)
3. [Gestionnaire de Thèmes](#-gestionnaire-de-thèmes)
4. [Stratège de Contenu](#-stratège-de-contenu)
5. [Rédacteur de Blog](#-rédacteur-de-blog)
6. [Créateur de Contenu Social](#-créateur-de-contenu-social)
7. [Créateur Visuel](#-créateur-visuel)
8. [Validateur](#-validateur)

## 🔹 Agent de Base

**Fichier**: `agents/base_agent.py`

Classe de base abstraite pour tous les agents du système.

### Fonctionnalités
- Gestion des configurations communes
- Initialisation du modèle de langage
- Gestion des erreres de base
- Journalisation

### Utilisation
```python
class MonAgent(BaseAgent):
    def __init__(self, model=None, **kwargs):
        super().__init__(model=model, **kwargs)
        # Initialisation spécifique
```

## 📄 Analyseur PDF

**Fichier**: `agents/pdf_analyzer.py`

Extrait et analyse le contenu des fichiers PDF.

### Fonctionnalités
- Extraction de texte depuis les PDF
- Analyse sémantique du contenu
- Identification des concepts clés
- Génération de résumés

### Méthodes Clés
- `analyze_pdf(pdf_path)`: Analyse un fichier PDF
- `extract_text(pdf_path)`: Extrait le texte brut
- `analyze_content(text)`: Analyse sémantique

## 🎨 Gestionnaire de Thèmes

**Fichier**: `agents/theme_manager.py`

Gère la cohérence thématique du contenu généré.

### Fonctionnalités
- Suivi des thèmes abordés
- Détection des répétitions
- Suggestions de sujets sous-représentés
- Analyse de la progression thématique

## 📊 Stratège de Contenu

**Fichier**: `agents/content_strategy.py`

Élabore la stratégie éditoriale globale.

### Fonctionnalités
- Planification du calendrier éditorial
- Sélection des sujets
- Adaptation au public cible
- Optimisation SEO

## ✍️ Rédacteur de Blog

**Fichier**: `agents/blog_writer.py`

Génère des articles de blog complets en Markdown avec métadonnées structurées.

### Fonctionnalités
- Rédaction d'articles (1500-2000 mots) au format Markdown
- Structure optimisée pour le référencement avec balises H1-H6
- Gestion intelligente des réponses (JSON et Markdown)
- Extraction automatique des métadonnées (titre, description, mots-clés)
- Génération de contenu structuré avec en-têtes, listes et mise en forme
- Gestion des erreurs et validation du contenu généré
- Journalisation détaillée pour le débogage

## 📱 Créateur de Contenu Social

**Fichier**: `agents/social_creator.py`

Crée des publications pour les réseaux sociaux.

### Fonctionnalités
- Génération de posts Facebook
- Adaptation du contenu aux plateformes
- Planification des publications
- Optimisation pour l'engagement

## 🖼️ Créateur Visuel

**Fichier**: `agents/visual_creator.py`

Génère des prompts détaillés pour la création d'éléments visuels, incluant des métadonnées complètes en français et en anglais.

### Fonctionnalités
- Génération de prompts structurés pour la création de visuels
- Création de métadonnées bilingues (français/anglais)
- Spécifications techniques précises pour les visuels
- Gestion de différents types de visuels (infographies, diagrammes, illustrations, etc.)
- Instructions créatives détaillées pour les concepteurs

### Métadonnées Incluses
- Nom de fichier standardisé
- Balises alt descriptives
- Légendes bilingues
- Descriptions détaillées
- Instructions de style et d'esthétique

## ✅ Validateur

**Fichier**: `agents/validator.py`

Valide la qualité et la conformité du contenu généré.

### Fonctionnalités
- Vérification de la qualité rédactionnelle
- Validation éthique
- Contrôle de la cohérence thématique
- Génération de rapports détaillés

## 🔄 Workflow d'Intégration

Tous les agents sont conçus pour fonctionner ensemble dans un pipeline de traitement :

1. L'Analyseur PDF extrait le contenu
2. Le Gestionnaire de Thèmes analyse la cohérence
3. Le Stratège de Contenu élabore le plan éditorial
4. Le Rédacteur de Blog crée le contenu principal
5. Le Créateur de Contenu Social génère les publications
6. Le Créateur Visuel produit les éléments graphiques
7. Le Validateur assure la qualité finale

## 🛠 Bonnes Pratiques

- Toujours initialiser les agents avec les paramètres appropriés
- Gérer correctement les erreurs et les exceptions
- Documenter tout nouveau paramètre ou comportement
- Tester chaque agent de manière isolée avant intégration
