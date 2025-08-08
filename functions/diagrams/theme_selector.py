#!/usr/bin/env python3
"""
PlantUML Theme Selector Module
Supports 31 official PlantUML themes from https://the-lum.github.io/puml-themes-gallery/
"""

import re
from typing import List, Optional

# Complete list of supported PlantUML themes
SUPPORTED_THEMES = [
    "amiga", "aws-orange", "black-knight", "bluegray", "blueprint", "carbon-gray", "cerulean",
    "cloudscape-design", "crt-amber", "cyborg", "hacker", "lightgray", "mars", "materia", "metal",
    "mimeograph", "minty", "mono", "none", "plain", "reddress-darkblue", "reddress-lightblue",
    "sandstone", "silver", "sketchy", "spacelab", "Sunlust", "superhero", "toy", "united", "vibrant"
]

def inject_theme(puml_code: str, theme_name: str) -> str:
    """
    Inject a theme into PlantUML code
    
    Args:
        puml_code: PlantUML diagram code
        theme_name: Name of the theme to inject
        
    Returns:
        PlantUML code with theme injected
    """
    # If theme already exists, return as-is
    if "!theme" in puml_code:
        return puml_code
    
    # Validate theme name
    if theme_name not in SUPPORTED_THEMES:
        theme_name = "plain"
    
    # Inject theme after @startuml
    return puml_code.replace("@startuml", f"@startuml\n!theme {theme_name}", 1)

def replace_theme(puml_code: str, new_theme: str) -> str:
    """
    Replace existing theme with a new one
    
    Args:
        puml_code: PlantUML diagram code
        new_theme: Name of the new theme
        
    Returns:
        PlantUML code with updated theme
    """
    # Remove existing theme directive if present
    puml_code = re.sub(r'!theme\s+\w+\s*\n?', '', puml_code)
    
    # Inject new theme
    return inject_theme(puml_code, new_theme)

def get_theme_description(theme_name: str) -> str:
    """
    Get a description of the theme characteristics
    
    Args:
        theme_name: Name of the theme
        
    Returns:
        Description of the theme
    """
    theme_descriptions = {
        "amiga": "Retro Amiga computer inspired theme with classic colors",
        "aws-orange": "AWS cloud services orange and dark theme",
        "black-knight": "Dark medieval theme with gold accents",
        "bluegray": "Professional blue-gray color scheme",
        "blueprint": "Technical blueprint style with grid background",
        "carbon-gray": "Carbon design system inspired gray theme",
        "cerulean": "Bright cerulean blue theme",
        "cloudscape-design": "AWS Cloudscape design system theme",
        "crt-amber": "Classic CRT amber monitor theme",
        "cyborg": "Dark cyberpunk-inspired theme",
        "hacker": "Matrix-style green on black hacker theme",
        "lightgray": "Light gray minimalist theme",
        "mars": "Mars red planet inspired theme",
        "materia": "Material design inspired theme",
        "metal": "Metallic silver and gray theme",
        "mimeograph": "Vintage mimeograph purple theme",
        "minty": "Fresh mint green theme",
        "mono": "Monochrome black and white theme",
        "none": "No theme (PlantUML defaults)",
        "plain": "Plain default PlantUML theme",
        "reddress-darkblue": "Red dress with dark blue accents",
        "reddress-lightblue": "Red dress with light blue accents",
        "sandstone": "Warm sandstone brown theme",
        "silver": "Elegant silver theme",
        "sketchy": "Hand-drawn sketchy style theme",
        "spacelab": "Clean space laboratory theme",
        "Sunlust": "Warm sunset colors theme",
        "superhero": "Comic book superhero theme",
        "toy": "Playful toy-like colorful theme",
        "united": "United colors theme",
        "vibrant": "High contrast vibrant colors"
    }
    
    return theme_descriptions.get(theme_name, "Standard PlantUML theme")

def list_themes_formatted() -> str:
    """
    Get formatted list of all themes with descriptions
    
    Returns:
        Formatted string with all themes and descriptions
    """
    output = "Available PlantUML Themes:\n"
    output += "=" * 60 + "\n\n"
    
    for theme in SUPPORTED_THEMES:
        description = get_theme_description(theme)
        output += f"  {theme:<24} - {description}\n"
    
    return output

def validate_theme(theme_name: str) -> bool:
    """
    Check if a theme name is valid
    
    Args:
        theme_name: Name of the theme to validate
        
    Returns:
        True if theme is valid, False otherwise
    """
    return theme_name in SUPPORTED_THEMES

def get_theme_category(theme_name: str) -> str:
    """
    Categorize themes by style
    
    Args:
        theme_name: Name of the theme
        
    Returns:
        Category of the theme
    """
    categories = {
        "dark": ["black-knight", "carbon-gray", "cyborg", "hacker", "reddress-darkblue", "superhero"],
        "light": ["lightgray", "plain", "sandstone", "silver", "spacelab", "united"],
        "colorful": ["cerulean", "mars", "minty", "Sunlust", "toy", "vibrant"],
        "retro": ["amiga", "crt-amber", "mimeograph"],
        "technical": ["blueprint", "aws-orange", "cloudscape-design"],
        "artistic": ["sketchy", "materia"],
        "monochrome": ["mono", "metal"],
        "special": ["none", "bluegray", "reddress-lightblue"]
    }
    
    for category, themes in categories.items():
        if theme_name in themes:
            return category
    
    return "standard"

# Convenience function for CLI usage
def print_themes():
    """Print all available themes to console"""
    print(list_themes_formatted())

if __name__ == "__main__":
    # Test the module
    sample_puml = """@startuml
    Alice -> Bob: Hello
    @enduml"""
    
    # Test theme injection
    themed = inject_theme(sample_puml, "cyborg")
    print("Sample with cyborg theme:")
    print(themed)
    print("\nAll available themes:")
    print_themes()