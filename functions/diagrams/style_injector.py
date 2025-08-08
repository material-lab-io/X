#!/usr/bin/env python3
"""
PlantUML Style Injection Module
Automatically applies visual enhancements to PlantUML diagrams
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class PlantUMLStyleInjector:
    """
    Injects custom styles into PlantUML diagrams for visual enhancement
    """
    
    def __init__(self):
        """Initialize the style injector with available styles"""
        self.styles_dir = Path(__file__).parent / "styles"
        self.available_themes = ['dark', 'light', 'brand']
        self.available_layouts = ['vertical', 'horizontal']
        
        # Load style templates
        self.style_templates = self._load_style_templates()
        
        # Default configuration
        self.default_theme = 'brand'
        self.default_layout = 'vertical'
        self.enable_icons = True
        
    def _load_style_templates(self) -> Dict[str, str]:
        """Load all style templates from files"""
        templates = {}
        
        style_files = {
            'dark': 'style_dark.puml',
            'light': 'style_light.puml',
            'brand': 'style_brand.puml',
            'vertical': 'style_layout_vertical.puml',
            'horizontal': 'style_layout_horizontal.puml',
            'icons': 'style_icons.puml'
        }
        
        for key, filename in style_files.items():
            filepath = self.styles_dir / filename
            if filepath.exists():
                with open(filepath, 'r') as f:
                    templates[key] = f.read()
                logger.info(f"Loaded style template: {key}")
            else:
                logger.warning(f"Style template not found: {filepath}")
                
        return templates
    
    def inject_styles(self, 
                      plantuml_content: str,
                      theme: str = None,
                      layout: str = None,
                      enable_icons: bool = None,
                      diagram_type: str = None) -> str:
        """
        Inject styles into PlantUML content
        
        Args:
            plantuml_content: Original PlantUML diagram code
            theme: Theme to apply (dark/light/brand)
            layout: Layout orientation (vertical/horizontal)
            enable_icons: Whether to enable icon libraries
            diagram_type: Type of diagram for specific optimizations
            
        Returns:
            Enhanced PlantUML content with styles injected
        """
        # Use defaults if not specified
        theme = theme or self.default_theme
        layout = layout or self.default_layout
        enable_icons = enable_icons if enable_icons is not None else self.enable_icons
        
        # Validate inputs
        if theme not in self.available_themes:
            logger.warning(f"Unknown theme: {theme}, using default")
            theme = self.default_theme
            
        if layout not in self.available_layouts:
            logger.warning(f"Unknown layout: {layout}, using default")
            layout = self.default_layout
        
        # Detect diagram type if not provided
        if not diagram_type:
            diagram_type = self._detect_diagram_type(plantuml_content)
        
        # Build style injection
        style_injection = self._build_style_injection(theme, layout, enable_icons, diagram_type)
        
        # Inject styles into content
        enhanced_content = self._inject_into_content(plantuml_content, style_injection)
        
        # Apply diagram-specific optimizations
        enhanced_content = self._apply_diagram_optimizations(enhanced_content, diagram_type, theme)
        
        return enhanced_content
    
    def _detect_diagram_type(self, content: str) -> str:
        """Detect the type of PlantUML diagram from content"""
        content_lower = content.lower()
        
        if '@startsequence' in content_lower or 'participant' in content_lower:
            return 'sequence'
        elif '@startclass' in content_lower or 'class ' in content_lower:
            return 'class'
        elif '@startcomponent' in content_lower or 'component' in content_lower:
            return 'component'
        elif '@startactivity' in content_lower or 'start' in content_lower:
            return 'activity'
        elif '@startstate' in content_lower:
            return 'state'
        elif '@startusecase' in content_lower or 'usecase' in content_lower:
            return 'usecase'
        else:
            return 'generic'
    
    def _build_style_injection(self, 
                               theme: str, 
                               layout: str, 
                               enable_icons: bool,
                               diagram_type: str) -> str:
        """Build the complete style injection string"""
        injection_parts = []
        
        # Add theme styles
        if theme in self.style_templates:
            injection_parts.append(self.style_templates[theme])
        
        # Add layout styles
        if layout in self.style_templates:
            injection_parts.append(self.style_templates[layout])
        
        # Add icon support if enabled and relevant
        if enable_icons and self._should_include_icons(diagram_type):
            if 'icons' in self.style_templates:
                injection_parts.append(self._get_relevant_icons(diagram_type))
        
        # Add diagram-specific styles
        specific_styles = self._get_diagram_specific_styles(diagram_type, theme)
        if specific_styles:
            injection_parts.append(specific_styles)
        
        return '\n'.join(injection_parts)
    
    def _should_include_icons(self, diagram_type: str) -> bool:
        """Determine if icons should be included for this diagram type"""
        # Icons are most useful for component and deployment diagrams
        return diagram_type in ['component', 'deployment', 'generic']
    
    def _get_relevant_icons(self, diagram_type: str) -> str:
        """Get only relevant icon imports for the diagram type"""
        base_icons = """
' Core icon imports
!define ICONURL https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/sprites
!define DEVICONS2 https://raw.githubusercontent.com/tupadr3/plantuml-icon-font-sprites/master/devicons2
!define FONTAWESOME https://raw.githubusercontent.com/tupadr3/plantuml-icon-font-sprites/master/font-awesome-5
"""
        
        if diagram_type == 'component':
            return base_icons + """
' Component diagram icons
!includeurl DEVICONS2/docker.puml
!includeurl DEVICONS2/kubernetes.puml
!includeurl FONTAWESOME/server.puml
!includeurl FONTAWESOME/database.puml
"""
        elif diagram_type == 'deployment':
            return base_icons + """
' Deployment diagram icons
!define AWSPUML https://raw.githubusercontent.com/awslabs/aws-icons-for-plantuml/v18.0/dist
!includeurl AWSPUML/AWSCommon.puml
"""
        else:
            return base_icons
    
    def _get_diagram_specific_styles(self, diagram_type: str, theme: str) -> str:
        """Get diagram-type specific style overrides"""
        styles = []
        
        if diagram_type == 'sequence':
            styles.append("""
' Sequence diagram optimizations
skinparam sequence {
    ParticipantPadding 25
    BoxPadding 20
    ArrowFontSize 13
    LifeLineThickness 2
}
""")
        elif diagram_type == 'class':
            styles.append("""
' Class diagram optimizations
skinparam class {
    AttributeIconSize 14
    FontSize 14
    StereotypeFontSize 12
}
""")
        elif diagram_type == 'activity':
            styles.append("""
' Activity diagram optimizations
skinparam activity {
    DiamondFontSize 13
    ArrowFontSize 12
    BarColor.Sync #1da1f2
}
""")
        elif diagram_type == 'component':
            styles.append("""
' Component diagram optimizations
skinparam component {
    FontSize 14
    StereotypeFontSize 11
}
""")
        
        return '\n'.join(styles)
    
    def _inject_into_content(self, content: str, style_injection: str) -> str:
        """Inject styles into the PlantUML content"""
        # Find @startuml or variant
        start_pattern = r'(@start[a-z]*)'
        
        # Check if content already has @startuml
        if re.search(start_pattern, content, re.IGNORECASE):
            # Inject after the @startuml line
            enhanced = re.sub(
                start_pattern,
                r'\1\n\n' + style_injection + '\n',
                content,
                count=1,
                flags=re.IGNORECASE
            )
        else:
            # Add @startuml and styles at the beginning
            enhanced = f"@startuml\n\n{style_injection}\n\n{content}\n@enduml"
        
        return enhanced
    
    def _apply_diagram_optimizations(self, content: str, diagram_type: str, theme: str) -> str:
        """Apply diagram-specific optimizations to content"""
        
        # Add direction hints for better layout
        if diagram_type == 'sequence' and 'left to right direction' not in content:
            # Sequences usually work better top-to-bottom (default)
            pass
        elif diagram_type == 'component' and 'direction' not in content:
            # Components often benefit from left-to-right
            content = content.replace('@startuml', '@startuml\nleft to right direction')
        
        # Add title styling if title exists
        if 'title ' in content.lower():
            title_style = """
skinparam title {
    FontSize 18
    FontStyle bold
    FontColor #1da1f2
    BorderThickness 0
}
"""
            content = self._inject_after_start(content, title_style)
        
        # Add note styling for better readability
        if 'note ' in content.lower():
            if theme == 'dark':
                note_style = "skinparam noteFontColor #ffffff"
            else:
                note_style = "skinparam noteFontColor #2d3436"
            content = self._inject_after_start(content, note_style)
        
        return content
    
    def _inject_after_start(self, content: str, injection: str) -> str:
        """Helper to inject content after @startuml"""
        start_pattern = r'(@start[a-z]*)'
        return re.sub(
            start_pattern,
            r'\1\n' + injection,
            content,
            count=1,
            flags=re.IGNORECASE
        )
    
    def get_enhanced_filename(self, original_filename: str, theme: str) -> str:
        """Generate filename for enhanced version"""
        path = Path(original_filename)
        name_parts = path.stem.split('_')
        
        # Insert theme identifier
        enhanced_name = f"{name_parts[0]}_enhanced_{theme}_{'_'.join(name_parts[1:])}"
        
        return str(path.parent / "enhanced" / f"{enhanced_name}{path.suffix}")
    
    def batch_enhance(self, 
                     contents: List[str],
                     themes: List[str] = None,
                     layout: str = None) -> List[str]:
        """Enhance multiple diagrams in batch"""
        themes = themes or [self.default_theme] * len(contents)
        
        enhanced_contents = []
        for content, theme in zip(contents, themes):
            enhanced = self.inject_styles(content, theme=theme, layout=layout)
            enhanced_contents.append(enhanced)
            
        return enhanced_contents


# Convenience functions
def enhance_plantuml(content: str, theme: str = 'brand', layout: str = 'vertical') -> str:
    """Quick function to enhance PlantUML content"""
    injector = PlantUMLStyleInjector()
    return injector.inject_styles(content, theme=theme, layout=layout)


def auto_enhance(content: str) -> Dict[str, str]:
    """Generate enhanced versions in all themes"""
    injector = PlantUMLStyleInjector()
    
    results = {}
    for theme in injector.available_themes:
        results[theme] = injector.inject_styles(content, theme=theme)
    
    return results


if __name__ == "__main__":
    # Test the style injector
    test_content = """
    @startuml
    participant Client
    participant Server
    participant Database
    
    Client -> Server: Request
    Server -> Database: Query
    Database --> Server: Result
    Server --> Client: Response
    @enduml
    """
    
    injector = PlantUMLStyleInjector()
    
    # Test with different themes
    for theme in ['dark', 'light', 'brand']:
        enhanced = injector.inject_styles(test_content, theme=theme)
        print(f"\n{'='*60}")
        print(f"Theme: {theme}")
        print('='*60)
        print(enhanced[:500] + "..." if len(enhanced) > 500 else enhanced)