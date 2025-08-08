#!/usr/bin/env python3
"""
Thread-Aware Multi-Diagram Generator
Generates a series of consistent PlantUML diagrams from multi-section input
Perfect for technical tutorials and system breakdowns in tweet threads
"""

import os
import re
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
import hashlib

# Import existing modules
from plantuml_generator import PlantUMLGenerator
from style_injector import PlantUMLStyleInjector
from ai_optimizer import PlantUMLAIOptimizer
from theme_selector import inject_theme, SUPPORTED_THEMES

logger = logging.getLogger(__name__)

class ThreadDiagramGenerator:
    """
    Generates multiple PlantUML diagrams from sectioned content
    Maintains consistency across diagrams for thread coherence
    """
    
    def __init__(self, theme: str = 'brand', optimize: bool = True, plantuml_theme: str = 'plain'):
        """
        Initialize thread diagram generator
        
        Args:
            theme: Visual theme to apply consistently (for style_injector)
            optimize: Whether to apply AI optimization
            plantuml_theme: Official PlantUML theme to use
        """
        self.theme = theme
        self.optimize = optimize
        self.plantuml_theme = plantuml_theme if plantuml_theme in SUPPORTED_THEMES else 'plain'
        
        # Initialize component generators
        self.plantuml_generator = PlantUMLGenerator()
        self.style_injector = PlantUMLStyleInjector()
        self.ai_optimizer = PlantUMLAIOptimizer()
        
        # Output directory - organized by theme
        if self.plantuml_theme != 'plain':
            self.output_dir = Path(f"generated_tweets/diagrams/plantuml/themed/{self.plantuml_theme}")
        else:
            self.output_dir = Path("generated_tweets/diagrams/plantuml/thread_diagrams")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Persistent label memory for consistency
        self.label_memory = {
            'services': {},
            'databases': {},
            'components': {},
            'participants': {},
            'classes': {}
        }
        
        # Consistent settings
        self.default_direction = 'top to bottom direction'
        self.default_layout = 'vertical'
        
    def generate_thread(self, input_content: str, input_format: str = 'auto') -> Dict[str, Any]:
        """
        Generate a series of diagrams from multi-section input
        
        Args:
            input_content: Multi-section content (Markdown, JSON, or plain text)
            input_format: Format of input ('markdown', 'json', 'text', 'auto')
            
        Returns:
            Dict with generation results and file paths
        """
        # Detect format if auto
        if input_format == 'auto':
            input_format = self._detect_format(input_content)
        
        # Parse sections based on format
        sections = self._parse_sections(input_content, input_format)
        
        if not sections:
            return {
                'success': False,
                'error': 'No sections found in input'
            }
        
        # Generate diagrams for each section
        results = {
            'success': True,
            'total_sections': len(sections),
            'diagrams': [],
            'theme': self.theme,
            'optimized': self.optimize,
            'timestamp': datetime.now().isoformat()
        }
        
        for idx, section in enumerate(sections, 1):
            diagram_result = self._generate_section_diagram(
                section=section,
                section_num=idx,
                total_sections=len(sections)
            )
            results['diagrams'].append(diagram_result)
        
        # Generate index file
        self._generate_index_file(results)
        
        return results
    
    def _detect_format(self, content: str) -> str:
        """Detect input format automatically"""
        content_stripped = content.strip()
        
        # Check for JSON
        if content_stripped.startswith('[') or content_stripped.startswith('{'):
            try:
                json.loads(content_stripped)
                return 'json'
            except:
                pass
        
        # Check for Markdown headers
        if '## ' in content or '### ' in content:
            return 'markdown'
        
        # Default to text
        return 'text'
    
    def _parse_sections(self, content: str, format_type: str) -> List[Dict[str, str]]:
        """Parse content into sections based on format"""
        sections = []
        
        if format_type == 'markdown':
            sections = self._parse_markdown_sections(content)
        elif format_type == 'json':
            sections = self._parse_json_sections(content)
        elif format_type == 'text':
            sections = self._parse_text_sections(content)
        else:
            # Auto-split for unstructured content
            sections = self._auto_split_sections(content)
        
        return sections
    
    def _parse_markdown_sections(self, content: str) -> List[Dict[str, str]]:
        """Parse Markdown with ## headers into sections"""
        sections = []
        
        # Split by ## headers
        pattern = r'##\s+(.+?)(?=##|\Z)'
        matches = re.findall(pattern, content, re.DOTALL)
        
        for match in matches:
            lines = match.strip().split('\n')
            if lines:
                # Extract title and content
                title = lines[0].strip()
                
                # Clean title (remove Step X: prefix if present)
                title_clean = re.sub(r'^Step\s+\d+:\s*', '', title)
                
                # Extract description
                description = '\n'.join(lines[1:]).strip()
                
                # Detect diagram type from content
                diagram_type = self._detect_diagram_type(description)
                
                sections.append({
                    'title': title_clean,
                    'description': description,
                    'type': diagram_type,
                    'raw': match
                })
        
        return sections
    
    def _parse_json_sections(self, content: str) -> List[Dict[str, str]]:
        """Parse JSON array or object into sections"""
        sections = []
        
        try:
            data = json.loads(content)
            
            if isinstance(data, list):
                # Array of sections
                for item in data:
                    if isinstance(item, dict):
                        sections.append({
                            'title': item.get('title', 'Untitled'),
                            'description': item.get('description', ''),
                            'type': item.get('type', self._detect_diagram_type(item.get('description', ''))),
                            'raw': json.dumps(item)
                        })
                    elif isinstance(item, str):
                        # Simple string array
                        sections.append({
                            'title': f'Section {len(sections) + 1}',
                            'description': item,
                            'type': self._detect_diagram_type(item),
                            'raw': item
                        })
            elif isinstance(data, dict):
                # Object with sections
                if 'sections' in data:
                    return self._parse_json_sections(json.dumps(data['sections']))
                else:
                    # Single section
                    sections.append({
                        'title': data.get('title', 'Untitled'),
                        'description': data.get('description', ''),
                        'type': data.get('type', 'generic'),
                        'raw': content
                    })
        except json.JSONDecodeError:
            logger.error("Invalid JSON format")
        
        return sections
    
    def _parse_text_sections(self, content: str) -> List[Dict[str, str]]:
        """Parse plain text with simple separators"""
        sections = []
        
        # Try to split by common separators
        separators = ['\n---\n', '\n===\n', '\n\n\n']
        
        parts = [content]
        for separator in separators:
            if separator in content:
                parts = content.split(separator)
                break
        
        for idx, part in enumerate(parts, 1):
            if part.strip():
                # Extract first line as title if possible
                lines = part.strip().split('\n')
                if len(lines) > 1:
                    title = lines[0].strip()
                    description = '\n'.join(lines[1:]).strip()
                else:
                    title = f'Section {idx}'
                    description = part.strip()
                
                sections.append({
                    'title': title,
                    'description': description,
                    'type': self._detect_diagram_type(description),
                    'raw': part
                })
        
        return sections
    
    def _auto_split_sections(self, content: str) -> List[Dict[str, str]]:
        """Intelligently split unstructured content into logical sections"""
        sections = []
        
        # Look for natural breaks
        paragraphs = content.split('\n\n')
        
        # Group into logical sections
        current_section = []
        section_count = 0
        
        for para in paragraphs:
            if para.strip():
                # Check if this looks like a new topic
                if self._is_new_topic(para) and current_section:
                    # Save current section
                    section_count += 1
                    combined = '\n\n'.join(current_section)
                    sections.append({
                        'title': self._extract_topic_title(combined, section_count),
                        'description': combined,
                        'type': self._detect_diagram_type(combined),
                        'raw': combined
                    })
                    current_section = [para]
                else:
                    current_section.append(para)
        
        # Add last section
        if current_section:
            section_count += 1
            combined = '\n\n'.join(current_section)
            sections.append({
                'title': self._extract_topic_title(combined, section_count),
                'description': combined,
                'type': self._detect_diagram_type(combined),
                'raw': combined
            })
        
        return sections
    
    def _is_new_topic(self, text: str) -> bool:
        """Detect if text represents a new topic"""
        # Check for topic indicators
        indicators = [
            r'^(Step|Phase|Part|Section)\s+\d+',
            r'^(First|Second|Third|Next|Finally|Then)',
            r'^\d+\.',
            r'^[A-Z][^.!?]*:$'  # Title-like pattern
        ]
        
        for pattern in indicators:
            if re.match(pattern, text.strip(), re.IGNORECASE):
                return True
        
        return False
    
    def _extract_topic_title(self, text: str, section_num: int) -> str:
        """Extract or generate a title for a section"""
        lines = text.split('\n')
        
        # Check first line for title-like pattern
        first_line = lines[0].strip()
        if len(first_line) < 100 and (first_line.endswith(':') or re.match(r'^[A-Z]', first_line)):
            return first_line.rstrip(':')
        
        # Extract key concepts
        if 'authentication' in text.lower():
            return 'Authentication Flow'
        elif 'database' in text.lower():
            return 'Data Layer'
        elif 'api' in text.lower():
            return 'API Integration'
        elif 'deployment' in text.lower():
            return 'Deployment Architecture'
        else:
            return f'Section {section_num}'
    
    def _detect_diagram_type(self, content: str) -> str:
        """Detect appropriate diagram type from content"""
        content_lower = content.lower()
        
        # Keywords for different diagram types
        if any(word in content_lower for word in ['flow', 'request', 'response', 'sends', 'receives']):
            return 'sequence'
        elif any(word in content_lower for word in ['class', 'inheritance', 'extends', 'implements']):
            return 'class'
        elif any(word in content_lower for word in ['component', 'module', 'service', 'system']):
            return 'component'
        elif any(word in content_lower for word in ['deploy', 'server', 'node', 'cluster']):
            return 'deployment'
        elif any(word in content_lower for word in ['activity', 'process', 'workflow', 'step']):
            return 'activity'
        elif any(word in content_lower for word in ['state', 'transition', 'status']):
            return 'state'
        else:
            return 'generic'
    
    def _generate_section_diagram(self, section: Dict, section_num: int, total_sections: int) -> Dict[str, Any]:
        """Generate a single diagram for a section"""
        
        # Generate PlantUML content from description
        plantuml_content = self._description_to_plantuml(
            description=section['description'],
            diagram_type=section['type'],
            section_num=section_num,
            total_sections=total_sections,
            title=section['title']
        )
        
        # Apply consistent labeling from memory
        plantuml_content = self._apply_label_consistency(plantuml_content)
        
        # Apply AI optimization if enabled
        if self.optimize:
            try:
                optimization_result = self.ai_optimizer.optimize(
                    plantuml_content,
                    context=section['title']
                )
                if optimization_result['improved']:
                    plantuml_content = optimization_result['optimized']
            except Exception as e:
                logger.warning(f"Optimization failed for section {section_num}: {e}")
        
        # Inject PlantUML theme
        plantuml_content = inject_theme(plantuml_content, self.plantuml_theme)
        
        # Apply visual styling (if not using official theme or if theme is 'plain')
        if self.plantuml_theme == 'plain':
            plantuml_content = self.style_injector.inject_styles(
                plantuml_content,
                theme=self.theme,
                layout=self.default_layout,
                enable_icons=True,
                diagram_type=section['type']
            )
        
        # Generate filename
        title_slug = re.sub(r'[^a-zA-Z0-9]+', '_', section['title'].lower())[:30]
        filename = f"thread_{section_num:02d}_{title_slug}.puml"
        filepath = self.output_dir / filename
        
        # Save PlantUML file
        with open(filepath, 'w') as f:
            f.write(plantuml_content)
        
        # Generate PNG using PlantUML generator
        png_result = self.plantuml_generator.generate_from_content(
            content=plantuml_content,
            topic=section['title'],
            theme=self.theme,
            optimize_layout=False  # Already optimized
        )
        
        return {
            'section_num': section_num,
            'title': section['title'],
            'type': section['type'],
            'puml_file': str(filepath),
            'png_file': png_result.get('path') if png_result.get('success') else None,
            'success': png_result.get('success', False),
            'content_preview': plantuml_content[:200] + '...' if len(plantuml_content) > 200 else plantuml_content
        }
    
    def _description_to_plantuml(self, description: str, diagram_type: str, 
                                 section_num: int, total_sections: int, title: str) -> str:
        """Convert text description to PlantUML code"""
        
        # Start with basic structure
        lines = ['@startuml']
        
        # Add consistent direction
        lines.append(self.default_direction)
        
        # Add title with thread position
        lines.append(f'title Step {section_num} of {total_sections} - {title}')
        lines.append('')
        
        # Generate content based on diagram type
        if diagram_type == 'sequence':
            lines.extend(self._generate_sequence_content(description))
        elif diagram_type == 'component':
            lines.extend(self._generate_component_content(description))
        elif diagram_type == 'class':
            lines.extend(self._generate_class_content(description))
        elif diagram_type == 'activity':
            lines.extend(self._generate_activity_content(description))
        else:
            lines.extend(self._generate_generic_content(description))
        
        lines.append('@enduml')
        
        return '\n'.join(lines)
    
    def _generate_sequence_content(self, description: str) -> List[str]:
        """Generate sequence diagram content from description"""
        lines = []
        
        # Extract entities and interactions
        entities = self._extract_entities(description)
        interactions = self._extract_interactions(description)
        
        # Add participants
        for entity in entities[:6]:  # Limit to 6 for readability
            lines.append(f'participant {entity}')
        
        lines.append('')
        
        # Add interactions
        for interaction in interactions[:10]:  # Limit interactions
            lines.append(interaction)
        
        # Add from memory if no interactions found
        if not interactions:
            lines.extend([
                'Client -> Server: Request',
                'Server -> Database: Query',
                'Database --> Server: Response',
                'Server --> Client: Result'
            ])
        
        return lines
    
    def _generate_component_content(self, description: str) -> List[str]:
        """Generate component diagram content from description"""
        lines = []
        
        # Extract components
        components = self._extract_components(description)
        
        # Group by type
        ui_components = []
        service_components = []
        data_components = []
        
        for comp in components[:9]:  # Limit total components
            comp_lower = comp.lower()
            if any(word in comp_lower for word in ['ui', 'frontend', 'client', 'web']):
                ui_components.append(comp)
            elif any(word in comp_lower for word in ['database', 'db', 'storage', 'cache']):
                data_components.append(comp)
            else:
                service_components.append(comp)
        
        # Add grouped components
        if ui_components:
            lines.append('package "Frontend" {')
            for comp in ui_components:
                lines.append(f'  component [{comp}]')
            lines.append('}')
        
        if service_components:
            lines.append('package "Services" {')
            for comp in service_components:
                lines.append(f'  component [{comp}]')
            lines.append('}')
        
        if data_components:
            lines.append('package "Data Layer" {')
            for comp in data_components:
                lines.append(f'  database [{comp}]')
            lines.append('}')
        
        # Add some connections
        if len(components) >= 2:
            lines.append('')
            lines.append(f'[{components[0]}] --> [{components[1]}]')
        
        return lines
    
    def _generate_class_content(self, description: str) -> List[str]:
        """Generate class diagram content from description"""
        lines = []
        
        # Extract class-like entities
        classes = self._extract_classes(description)
        
        for cls in classes[:5]:  # Limit classes
            lines.extend([
                f'class {cls} {{',
                '  +id: String',
                '  +name: String',
                f'  +process(): void',
                '}'
            ])
        
        # Add relationships if multiple classes
        if len(classes) >= 2:
            lines.append(f'{classes[0]} --> {classes[1]} : uses')
        
        return lines
    
    def _generate_activity_content(self, description: str) -> List[str]:
        """Generate activity diagram content from description"""
        lines = []
        
        # Extract steps
        steps = self._extract_steps(description)
        
        lines.append('start')
        
        for step in steps[:8]:  # Limit steps
            lines.append(f':{step};')
        
        lines.append('stop')
        
        return lines
    
    def _generate_generic_content(self, description: str) -> List[str]:
        """Generate generic diagram content"""
        # Default to component style
        return self._generate_component_content(description)
    
    def _extract_entities(self, text: str) -> List[str]:
        """Extract entity names from text"""
        entities = []
        
        # Look for capitalized words that might be entities
        words = re.findall(r'\b[A-Z][a-zA-Z]+(?:Service|Server|Client|API|DB|System|Module)?\b', text)
        
        for word in words:
            if word not in entities and len(word) > 2:
                entities.append(word)
                # Store in memory
                self.label_memory['participants'][word.lower()] = word
        
        # Add defaults if too few
        if len(entities) < 3:
            entities.extend(['Client', 'Server', 'Database'])
        
        return entities[:8]  # Limit to 8
    
    def _extract_interactions(self, text: str) -> List[str]:
        """Extract interactions from text"""
        interactions = []
        
        # Look for action words
        patterns = [
            r'(\w+)\s+(sends?|calls?|requests?|queries?|returns?|responds?)\s+(?:to\s+)?(\w+)',
            r'(\w+)\s+(->|-->)\s+(\w+)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match) >= 3:
                    actor1 = match[0].capitalize()
                    actor2 = match[2].capitalize()
                    action = match[1]
                    interactions.append(f'{actor1} -> {actor2}: {action}')
        
        return interactions[:10]
    
    def _extract_components(self, text: str) -> List[str]:
        """Extract component names from text"""
        components = []
        
        # Look for component-like terms
        patterns = [
            r'\b([A-Z][a-zA-Z]+(?:Service|Component|Module|System|Server|Client|API|Gateway|Database|Cache))\b',
            r'\b(UI|API|DB|Auth|Payment|Order|User|Admin|Frontend|Backend)\b'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if match not in components:
                    components.append(match)
                    # Store in memory
                    self.label_memory['components'][match.lower()] = match
        
        # Add defaults if needed
        if not components:
            components = ['Frontend', 'APIGateway', 'Service', 'Database']
        
        return components[:12]
    
    def _extract_classes(self, text: str) -> List[str]:
        """Extract class names from text"""
        classes = []
        
        # Look for class-like terms
        words = re.findall(r'\b[A-Z][a-zA-Z]+(?:Class|Model|Entity|Service|Controller|Repository)?\b', text)
        
        for word in words:
            if word not in classes and len(word) > 3:
                classes.append(word)
                self.label_memory['classes'][word.lower()] = word
        
        # Defaults
        if not classes:
            classes = ['User', 'Order', 'Product']
        
        return classes[:8]
    
    def _extract_steps(self, text: str) -> List[str]:
        """Extract process steps from text"""
        steps = []
        
        # Look for numbered items or action phrases
        patterns = [
            r'\d+\.\s+([^.\n]+)',
            r'(?:First|Then|Next|Finally),?\s+([^.\n]+)',
            r'(?:Step\s+\d+:?\s+)?([A-Z][^.\n]{10,50})'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                step = match.strip()
                if step and len(step) < 50:
                    steps.append(step)
        
        # Defaults
        if not steps:
            steps = ['Initialize', 'Process Request', 'Validate', 'Execute', 'Return Response']
        
        return steps[:10]
    
    def _apply_label_consistency(self, plantuml_content: str) -> str:
        """Apply consistent labeling across diagrams"""
        
        # Replace generic terms with remembered specific ones
        for category, labels in self.label_memory.items():
            for key, value in labels.items():
                # Case-insensitive replacement
                pattern = re.compile(r'\b' + re.escape(key) + r'\b', re.IGNORECASE)
                plantuml_content = pattern.sub(value, plantuml_content)
        
        return plantuml_content
    
    def _generate_index_file(self, results: Dict) -> None:
        """Generate an index file listing all diagrams"""
        index_path = self.output_dir / 'index.json'
        
        index_data = {
            'generated_at': results['timestamp'],
            'theme': results['theme'],
            'optimized': results['optimized'],
            'total_diagrams': results['total_sections'],
            'diagrams': []
        }
        
        for diagram in results['diagrams']:
            index_data['diagrams'].append({
                'number': diagram['section_num'],
                'title': diagram['title'],
                'type': diagram['type'],
                'puml_file': diagram['puml_file'],
                'png_file': diagram['png_file']
            })
        
        with open(index_path, 'w') as f:
            json.dump(index_data, f, indent=2)
        
        logger.info(f"Index file generated: {index_path}")


# Convenience functions
def generate_thread_diagrams(input_file: str, theme: str = 'brand', optimize: bool = True, plantuml_theme: str = 'plain') -> Dict[str, Any]:
    """Generate thread diagrams from a file"""
    generator = ThreadDiagramGenerator(theme=theme, optimize=optimize, plantuml_theme=plantuml_theme)
    
    # Read input file
    with open(input_file, 'r') as f:
        content = f.read()
    
    # Detect format from extension
    ext = Path(input_file).suffix.lower()
    if ext == '.md':
        format_type = 'markdown'
    elif ext == '.json':
        format_type = 'json'
    else:
        format_type = 'auto'
    
    return generator.generate_thread(content, format_type)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Thread-Aware Multi-Diagram Generator with Theme Support')
    parser.add_argument('--thread-diagram', type=str, metavar='FILE',
                       help='Input file containing multi-section content (MD/JSON/TXT)')
    parser.add_argument('--theme', default='plain', choices=SUPPORTED_THEMES,
                       help='PlantUML theme name (default: plain)')
    parser.add_argument('--list-themes', action='store_true',
                       help='List all available PlantUML themes')
    parser.add_argument('--optimize-layout', action='store_true',
                       help='Enable AI-aided layout optimization')
    parser.add_argument('--style-theme', default='brand', choices=['dark', 'light', 'brand'],
                       help='Visual style theme for custom styling (default: brand)')
    
    args = parser.parse_args()
    
    # Handle --list-themes flag
    if args.list_themes:
        from theme_selector import list_themes_formatted
        print(list_themes_formatted())
        exit()
    
    # Handle thread diagram generation
    if args.thread_diagram:
        result = generate_thread_diagrams(
            input_file=args.thread_diagram,
            theme=args.style_theme,
            optimize=args.optimize_layout,
            plantuml_theme=args.theme
        )
        
        if result['success']:
            print(f"✅ Generated {result['total_sections']} diagrams with theme: {args.theme}")
            for diagram in result['diagrams']:
                status = "✓" if diagram['success'] else "✗"
                print(f"  {status} {diagram['section_num']}. {diagram['title']} ({diagram['type']})")
                if diagram.get('puml_file'):
                    print(f"      → {diagram['puml_file']}")
        else:
            print(f"❌ Generation failed: {result.get('error')}")
    else:
        # Test with sample input
        sample_markdown = """
## Step 1: System Overview
The microservices architecture consists of a frontend client, API gateway, 
multiple services (Auth, User, Order), and shared databases.

## Step 2: Authentication Flow  
Client sends credentials to Auth Service through API Gateway.
Auth Service validates against User Database and returns JWT token.

## Step 3: Order Processing
Client submits order to Order Service.
Order Service validates user token, processes payment, and updates Order Database.
"""
        
        print(f"Testing with theme: {args.theme}")
        generator = ThreadDiagramGenerator(plantuml_theme=args.theme)
        result = generator.generate_thread(sample_markdown, 'markdown')
        
        print(f"Generated {result['total_sections']} diagrams")
        for diagram in result['diagrams']:
            print(f"  {diagram['section_num']}. {diagram['title']} ({diagram['type']})")
            print(f"     File: {diagram['puml_file']}")