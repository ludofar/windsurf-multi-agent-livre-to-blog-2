# 📜 Règles et Bonnes Pratiques

Ce document définit les règles et bonnes pratiques à suivre pour le développement et la maintenance du système multi-agent MTC.

## 🏗 Structure du Projet

```
.
├── agents/             # Code source des agents
│   ├── __init__.py
│   ├── base_agent.py   # Classe de base
│   └── ...            # Autres agents
├── docs/              # Documentation
├── input/             # Fichiers PDF en entrée
├── output/            # Contenu généré
│   ├── content/       # Contenu final
│   └── reports/       # Rapports d'exécution
├── tests/             # Tests automatisés
├── .env.example       # Configuration d'exemple
├── .gitignore
├── daily_workflow.py  # Point d'entrée principal
├── main.py           # Script d'analyse ponctuelle
└── README.md         # Documentation principale
```

## 🧩 Règles pour les Agents

### 1. Héritage et Structure
- Tous les agents doivent hériter de `BaseAgent`
- Implémenter les méthodes abstraites requises
- Documenter toutes les méthodes publiques avec des docstrings
- Utiliser des types de retour explicites
- Gérer correctement les erreurs et les exceptions

## 📝 Règles pour le Format Markdown

### 1. Structure des Articles
- Utiliser le format Markdown standard
- Inclure un en-tête YAML avec les métadonnées
- Structurer avec des titres (H1-H6) de manière cohérente
- Utiliser des listes à puces pour les énumérations
- Inclure des sauts de ligne entre les paragraphes

### 2. Mise en Forme
- **Gras** pour les termes importants
- *Italique* pour les citations ou l'emphase
- `code` pour les termes techniques
- Liens explicites avec descriptions
- Images avec texte alternatif

### 3. Métadonnées Requises
- `title`: Titre de l'article
- `description`: Résumé court
- `date`: Date de publication (format YYYY-MM-DD)
- `categories`: Liste des catégories
- `tags`: Mots-clés pertinents
- `reading_time`: Temps de lecture estimé
- Documenter chaque méthode avec docstring

### 2. Gestion des Erreurs
- Toujours utiliser des exceptions spécifiques
- Logger les erreurs de manière détaillée
- Fournir des messages d'erreur explicites

### 3. Configuration
- Utiliser des variables d'environnement pour les paramètres sensibles
- Fournir des valeurs par défaut raisonnables
- Valider les configurations au démarrage

## 📝 Règles de Code

### 1. Style de Code
- Suivre PEP 8
- Utiliser le formatage automatique avec Black
- Limiter les lignes à 88 caractères

### 2. Typage
- Utiliser les annotations de type Python
- Valider les types avec mypy
- Documenter les types complexes

### 3. Tests
- Écrire des tests unitaires pour chaque composant
- Maintenir une couverture de test > 80%
- Utiliser pytest pour l'exécution des tests

## 🔄 Workflow de Développement

### 1. Branches
- `main` : Branche de production stable
- `develop` : Branche d'intégration
- `feature/*` : Nouvelles fonctionnalités
- `fix/*` : Corrections de bugs

### 2. Commits
- Format : `type(portée) : description`
- Types : feat, fix, docs, style, refactor, test, chore
- Exemple : `feat(blog): ajout de la génération d'articles`

### 3. Revue de Code
- Toute modification doit passer par une Pull Request
- Au moins une approbation requise avant fusion
- Résoudre tous les commentaires avant de merger

## 🔒 Sécurité

### 1. Données Sensibles
- Ne jamais commiter de clés API
- Utiliser des variables d'environnement
- Mettre à jour régulièrement les dépendances

### 2. Authentification
- Valider toutes les entrées utilisateur
- Utiliser des tokens d'accès temporaires
- Implémenter une rotation des clés

## 📊 Métriques de Qualité

### 1. Couverture de Code
- Minimum 80% de couverture de test
- Suivre l'évolution de la dette technique
- Analyser la complexité cyclomatique

### 2. Performance
- Surveiller le temps d'exécution
- Optimiser les appels API coûteux
- Mettre en cache les résultats intermédiaires

## 🔧 Maintenance

### 1. Documentation
- Mettre à jour la documentation pour chaque modification
- Maintenir des exemples à jour
- Documenter les décisions d'architecture

### 2. Dépendances
- Mettre à jour régulièrement les dépendances
- Vérifier les vulnérabilités connues
- Documenter les changements de version majeurs

## 🤖 Intégration Continue

### 1. Pipelines
- Exécuter les tests à chaque commit
- Vérifier la qualité du code
- Déployer automatiquement en préproduction

### 2. Livraison Continue
- Versionner chaque déploiement
- Automatiser les rollbacks
- Surveiller les performances en production

## 📚 Ressources

- [Guide de style Python](https://www.python.org/dev/peps/pep-0008/)
- [Documentation Black](https://black.readthedocs.io/)
- [Guide de commit conventionnel](https://www.conventionalcommits.org/)

## 📝 Licence

Ce document est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.
