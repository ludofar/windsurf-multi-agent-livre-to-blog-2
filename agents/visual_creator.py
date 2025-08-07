from .base_agent import BaseAgent
from typing import Dict, Any
from enum import Enum
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class VisualType(str, Enum):
    INFOGRAPHIE = "infographie"
    DIAGRAMME = "diagramme"
    ILLUSTRATION = "illustration"
    GRAPHIQUE = "graphique"
    CITATION = "citation"
    CARROUSEL = "carrousel"
    SCHEMA = "schema"
    PHOTO = "photo"

class VisualStyle(str, Enum):
    MINIMALISTE = "minimaliste"
    TRADITIONNEL = "traditionnel_chinois"
    MODERNE = "moderne"
    AQUARELLE = "aquarelle"
    LIGNE = "ligne"
    REALISTE = "realiste"
    DESSIN_ANIME = "dessin_anime"
    FLAT_DESIGN = "flat_design"

class VisualCreatorAgent(BaseAgent):
    """
    Agent spécialisé dans la création de prompts pour la génération d'éléments visuels MTC.
    Génère des métadonnées pour les visuels incluant balise alt, légende et description.
    """
    
    def __init__(self, model: str = None):
        default_model = os.getenv('DEFAULT_MODEL', 'qwen/qwen3-coder')
        super().__init__(
            name="MTC Visual Prompt Generator",
            model=model or default_model
        )
    
    def generate_prompt(self, input_data: Dict[str, Any]) -> str:
        """
        Génère un prompt pour la création d'un visuel avec métadonnées complètes.
        
        Args:
            input_data: Doit contenir les clés suivantes :
                - type_visuel: Type de visuel (infographie, diagramme, etc.)
                - theme: Thème principal du visuel
                - style: Style visuel souhaité (optionnel)
                - elements: Liste des éléments à inclure dans le visuel
                - format_sortie: Format de sortie (jpg, png, etc.)
                
        Returns:
            str: Prompt formaté en markdown avec balises alt, légende et description
        """
        raw_type = input_data.get('type_visuel', 'infographie')
        try:
            type_visuel = VisualType(raw_type)
        except ValueError:
            logger.warning(f"Type de visuel invalide '{raw_type}', utilisation de la valeur par défaut.")
            type_visuel = VisualType.INFOGRAPHIE

        raw_style = input_data.get('style', 'moderne')
        try:
            style = VisualStyle(raw_style)
        except ValueError:
            logger.warning(f"Style visuel invalide '{raw_style}', utilisation de la valeur par défaut.")
            style = VisualStyle.MODERNE

        theme = input_data.get('theme', 'Médecine Traditionnelle Chinoise')
        elements = input_data.get('elements', [])
        format_sortie = input_data.get('format_sortie', 'jpg')
        
        # Construction du prompt en markdown
        prompt = f"""# 🖼️ Prompt pour la création d'un visuel MTC

## 📝 Métadonnées du visuel

### Français 🇫🇷
- **Type de visuel**: {type_visuel.value}
- **Thème principal**: {theme}
- **Style visuel**: {style.value}
- **Format de sortie**: {format_sortie.upper()}

### English 🇬🇧
- **Visual type**: {type_visuel.value}
- **Main theme**: {theme}
- **Visual style**: {style.value}
- **Output format**: {format_sortie.upper()}

## 📋 Instructions pour la création

Créez une image qui illustre parfaitement le thème "{theme}" dans un style {style.value}.

### Éléments à inclure:
"""
        
        # Ajout des éléments à inclure
        for element in elements:
            prompt += f"- {element}\n"
            
        # Génération du nom de fichier basé sur le thème et la date
        filename = f"{theme.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.{format_sortie}"
        
        prompt += f"""
## 📝 Métadonnées de l'image (à inclure dans le fichier .md)

```markdown
<!-- Français 🇫🇷 -->
### Métadonnées pour l'image
- **Nom du fichier**: `{filename}`
- **Balise Alt**: "{type_visuel.value} illustrant le thème {theme} en style {style.value}"
- **Légende**: "{type_visuel.value.capitalize()} sur le thème de {theme} en médecine traditionnelle chinoise"
- **Description**: "{type_visuel.value.capitalize()} détaillant les aspects clés de {theme} en MTC, avec un style {style.value}."

<!-- English 🇬🇧 -->
### Image metadata
- **Filename**: `{filename}`
- **Alt Text**: "{type_visuel.value} illustrating the theme {theme} in {style.value} style"
- **Caption**: "{type_visuel.value.capitalize()} on the theme of {theme} in traditional Chinese medicine"
- **Description**: "Detailed {type_visuel.value} about key aspects of {theme} in TCM, with {style.value} style."
```

## 🎨 Instructions créatives

1. **Style et esthétique**:
   - Utilisez un style {style.value} cohérent
   - Choisissez une palette de couleurs harmonieuse
   - Assurez-vous d'une excellente lisibilité du texte

2. **Éléments visuels**:
   - Intégrez des éléments graphiques pertinents pour la MTC
   - Utilisez des icônes et illustrations de haute qualité
   - Maintenez un équilibre visuel

3. **Accessibilité**:
   - Contraste suffisant pour la lisibilité
   - Texte de remplacement descriptif
   - Structure claire et hiérarchie visuelle

## 📤 Format de sortie

Générez une image au format {format_sortie.upper()} avec les caractéristiques suivantes:
- Haute résolution (minimum 1200x630px)
- Qualité optimisée pour le web
- Espace colorimétrique sRGB
"""
        
        return prompt
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Traite la demande de génération de prompt visuel.
        
        Args:
            input_data: Données d'entrée pour la génération
            
        Returns:
            Dict[str, Any]: Le prompt généré
        """
        return {
            'status': 'success',
            'prompt': self.generate_prompt(input_data)
        }
