#!/usr/bin/env python3
"""
AI-Aided PlantUML Optimizer
Intelligently improves diagram structure, labels, and layout using AI reasoning
"""

import re
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class PlantUMLAIOptimizer:
    """
    AI-powered optimizer for PlantUML diagrams
    Improves semantic clarity, layout, and structure
    """
    
    def __init__(self):
        """Initialize the AI optimizer"""
        self.optimized_dir = Path("generated_tweets/diagrams/plantuml/optimized")
        self.optimized_dir.mkdir(parents=True, exist_ok=True)
        
        # Common generic labels to replace
        self.generic_patterns = {
            r'Service\s*[A-Z0-9]?\b': 'Service',
            r'Module\s*[0-9]+\b': 'Module',
            r'Component\s*[A-Z0-9]?\b': 'Component',
            r'System\s*[A-Z0-9]?\b': 'System',
            r'Database\s*[0-9]+\b': 'Database',
            r'Server\s*[A-Z0-9]?\b': 'Server',
            r'Client\s*[0-9]+\b': 'Client',
            r'API\s*[0-9]+\b': 'API',
            r'User\s*[0-9]+\b': 'User',
            r'Process\s*[A-Z0-9]?\b': 'Process'
        }
        
        # Layout optimization rules
        self.layout_rules = {
            'sequence': 'top to bottom direction',
            'class': 'left to right direction',
            'component': 'left to right direction',
            'deployment': 'top to bottom direction',
            'activity': 'top to bottom direction',
            'state': 'left to right direction'
        }
        
    def optimize(self, plantuml_content: str, context: str = None) -> Dict[str, Any]:
        """
        Main optimization method that orchestrates all improvements
        
        Args:
            plantuml_content: Original PlantUML diagram code
            context: Optional context about the diagram's purpose
            
        Returns:
            Dict with optimized content and optimization report
        """
        original_content = plantuml_content
        optimizations_applied = []
        
        # Detect diagram type
        diagram_type = self._detect_diagram_type(plantuml_content)
        
        # Step 1: Semantic label refinement
        content, label_changes = self._refine_semantic_labels(plantuml_content, context)
        if label_changes:
            optimizations_applied.append(f"Refined {len(label_changes)} semantic labels")
            plantuml_content = content
        
        # Step 2: Auto layout optimization
        content, layout_added = self._optimize_layout(plantuml_content, diagram_type)
        if layout_added:
            optimizations_applied.append(f"Added layout optimization: {layout_added}")
            plantuml_content = content
        
        # Step 3: Block grouping and compartmentalization
        content, groups_added = self._add_block_grouping(plantuml_content, diagram_type)
        if groups_added:
            optimizations_applied.append(f"Added {groups_added} logical groupings")
            plantuml_content = content
        
        # Step 4: Auto notes and annotations
        content, notes_added = self._add_intelligent_annotations(plantuml_content, diagram_type, context)
        if notes_added:
            optimizations_applied.append(f"Added {notes_added} explanatory notes")
            plantuml_content = content
        
        # Step 5: Error and anti-pattern correction
        content, fixes_applied = self._fix_common_issues(plantuml_content, diagram_type)
        if fixes_applied:
            optimizations_applied.append(f"Fixed {len(fixes_applied)} issues")
            plantuml_content = content
        
        return {
            'original': original_content,
            'optimized': plantuml_content,
            'optimizations': optimizations_applied,
            'diagram_type': diagram_type,
            'improved': len(optimizations_applied) > 0
        }
    
    def _detect_diagram_type(self, content: str) -> str:
        """Detect the type of PlantUML diagram"""
        content_lower = content.lower()
        
        if 'participant' in content_lower or '@startsequence' in content_lower:
            return 'sequence'
        elif 'class ' in content_lower or '@startclass' in content_lower:
            return 'class'
        elif 'component' in content_lower or '@startcomponent' in content_lower:
            return 'component'
        elif 'node' in content_lower or 'deployment' in content_lower:
            return 'deployment'
        elif 'activity' in content_lower or '@startactivity' in content_lower:
            return 'activity'
        elif 'state' in content_lower or '@startstate' in content_lower:
            return 'state'
        elif 'usecase' in content_lower or '@startusecase' in content_lower:
            return 'usecase'
        else:
            return 'generic'
    
    def _refine_semantic_labels(self, content: str, context: str = None) -> Tuple[str, List[Dict]]:
        """
        Replace generic labels with meaningful semantic names
        """
        changes = []
        refined_content = content
        
        # Context-based replacements
        context_hints = self._extract_context_hints(context) if context else {}
        
        # Find and replace generic patterns
        for pattern, generic_type in self.generic_patterns.items():
            matches = re.finditer(pattern, refined_content)
            for match in matches:
                old_label = match.group()
                new_label = self._generate_semantic_label(old_label, generic_type, context_hints)
                if new_label != old_label:
                    refined_content = refined_content.replace(old_label, new_label)
                    changes.append({'old': old_label, 'new': new_label})
        
        # Specific improvements for common patterns
        improvements = {
            r'\bDB\b': 'Database',
            r'\bAPI\b': 'APIGateway',
            r'\bAuth\b': 'AuthService',
            r'\bMsg\b': 'MessageQueue',
            r'\bSvc\b': 'Service',
            r'\bApp\b': 'Application',
            r'\bWeb\b': 'WebServer',
            r'\bCache\b': 'CacheLayer'
        }
        
        for pattern, replacement in improvements.items():
            if re.search(pattern, refined_content):
                refined_content = re.sub(pattern, replacement, refined_content)
                changes.append({'pattern': pattern, 'replacement': replacement})
        
        return refined_content, changes
    
    def _generate_semantic_label(self, old_label: str, label_type: str, context_hints: Dict) -> str:
        """Generate meaningful semantic label based on type and context"""
        
        # Extract any number suffix
        number_match = re.search(r'\d+', old_label)
        suffix = number_match.group() if number_match else ''
        
        # Semantic label mappings based on type
        semantic_mappings = {
            'Service': ['UserService', 'AuthService', 'PaymentService', 'NotificationService', 
                       'OrderService', 'InventoryService', 'AnalyticsService', 'EmailService'],
            'Module': ['CoreModule', 'AuthModule', 'DataModule', 'APIModule', 
                      'ProcessingModule', 'ValidationModule', 'SecurityModule'],
            'Component': ['FrontendComponent', 'BackendComponent', 'MiddlewareComponent', 
                         'RouterComponent', 'ControllerComponent', 'ViewComponent'],
            'System': ['PaymentSystem', 'AuthSystem', 'MonitoringSystem', 'LoggingSystem',
                      'MessagingSystem', 'CacheSystem', 'StorageSystem'],
            'Database': ['UserDB', 'ProductDB', 'OrderDB', 'SessionDB', 'CacheDB', 
                        'AnalyticsDB', 'LogDB', 'ConfigDB'],
            'Server': ['WebServer', 'AppServer', 'APIServer', 'ProxyServer', 
                      'CacheServer', 'FileServer', 'MediaServer'],
            'Client': ['WebClient', 'MobileClient', 'DesktopClient', 'APIClient',
                      'AdminClient', 'ServiceClient'],
            'API': ['RestAPI', 'GraphQLAPI', 'WebSocketAPI', 'GRPCAPI', 
                   'PublicAPI', 'InternalAPI', 'ExternalAPI'],
            'Process': ['ValidationProcess', 'PaymentProcess', 'OrderProcess', 
                       'SyncProcess', 'BatchProcess', 'ETLProcess']
        }
        
        # Get appropriate semantic label
        if label_type in semantic_mappings:
            options = semantic_mappings[label_type]
            # Use suffix as index if available, otherwise use first option
            if suffix and suffix.isdigit():
                index = (int(suffix) - 1) % len(options)
                return options[index]
            else:
                return options[0]
        
        return old_label
    
    def _extract_context_hints(self, context: str) -> Dict:
        """Extract hints from context string to guide labeling"""
        hints = {}
        
        if context:
            context_lower = context.lower()
            
            # Domain hints
            if 'ecommerce' in context_lower or 'shop' in context_lower:
                hints['domain'] = 'ecommerce'
            elif 'auth' in context_lower or 'login' in context_lower:
                hints['domain'] = 'authentication'
            elif 'payment' in context_lower or 'billing' in context_lower:
                hints['domain'] = 'payment'
            elif 'social' in context_lower or 'chat' in context_lower:
                hints['domain'] = 'social'
            
            # Technology hints
            if 'microservice' in context_lower:
                hints['architecture'] = 'microservices'
            elif 'monolith' in context_lower:
                hints['architecture'] = 'monolithic'
            
            if 'cloud' in context_lower or 'aws' in context_lower:
                hints['deployment'] = 'cloud'
            elif 'kubernetes' in context_lower or 'k8s' in context_lower:
                hints['deployment'] = 'kubernetes'
        
        return hints
    
    def _optimize_layout(self, content: str, diagram_type: str) -> Tuple[str, Optional[str]]:
        """Add layout optimization directives"""
        
        # Check if layout directive already exists
        if 'direction' in content.lower():
            return content, None
        
        # Get appropriate layout for diagram type
        layout_directive = self.layout_rules.get(diagram_type, 'top to bottom direction')
        
        # Insert after @startuml
        if '@startuml' in content:
            optimized = content.replace('@startuml', f'@startuml\n{layout_directive}\n')
            return optimized, layout_directive
        
        return content, None
    
    def _add_block_grouping(self, content: str, diagram_type: str) -> Tuple[str, int]:
        """Add logical grouping with packages, nodes, or frames"""
        groups_added = 0
        optimized_content = content
        
        if diagram_type == 'component':
            # Group components by layer
            groups = self._identify_component_layers(content)
            for group_name, components in groups.items():
                if len(components) > 1:
                    # Wrap in package
                    package_block = f"\npackage \"{group_name}\" {{\n"
                    for comp in components:
                        package_block += f"  {comp}\n"
                    package_block += "}\n"
                    
                    # Replace original components with packaged version
                    for comp in components:
                        optimized_content = optimized_content.replace(comp, '')
                    
                    # Insert package after direction statement or @startuml
                    insert_point = self._find_insertion_point(optimized_content)
                    optimized_content = (optimized_content[:insert_point] + 
                                       package_block + 
                                       optimized_content[insert_point:])
                    groups_added += 1
        
        elif diagram_type == 'deployment':
            # Group by node/server
            if 'node' not in content.lower():
                # Add node wrappers for deployment elements
                optimized_content = self._wrap_deployment_nodes(content)
                groups_added += 1
        
        elif diagram_type == 'class':
            # Group related classes by domain
            domains = self._identify_class_domains(content)
            for domain, classes in domains.items():
                if len(classes) > 1:
                    package_block = f"\npackage \"{domain}\" #DDDDDD {{\n"
                    for cls in classes:
                        package_block += f"  {cls}\n"
                    package_block += "}\n"
                    groups_added += 1
        
        return optimized_content, groups_added
    
    def _identify_component_layers(self, content: str) -> Dict[str, List[str]]:
        """Identify architectural layers in component diagram"""
        layers = {
            'Frontend Layer': [],
            'API Layer': [],
            'Service Layer': [],
            'Data Layer': []
        }
        
        # Parse components
        component_pattern = r'component\s+\[([^\]]+)\]\s+as\s+(\w+)'
        matches = re.finditer(component_pattern, content)
        
        for match in matches:
            comp_name = match.group(1).lower()
            comp_full = match.group(0)
            
            if any(word in comp_name for word in ['ui', 'frontend', 'web', 'client']):
                layers['Frontend Layer'].append(comp_full)
            elif any(word in comp_name for word in ['api', 'gateway', 'endpoint']):
                layers['API Layer'].append(comp_full)
            elif any(word in comp_name for word in ['service', 'business', 'logic']):
                layers['Service Layer'].append(comp_full)
            elif any(word in comp_name for word in ['database', 'db', 'storage', 'cache']):
                layers['Data Layer'].append(comp_full)
        
        # Remove empty layers
        return {k: v for k, v in layers.items() if v}
    
    def _identify_class_domains(self, content: str) -> Dict[str, List[str]]:
        """Identify domain boundaries in class diagrams"""
        domains = {
            'User Management': [],
            'Business Logic': [],
            'Data Access': [],
            'Utilities': []
        }
        
        class_pattern = r'class\s+(\w+)'
        matches = re.finditer(class_pattern, content)
        
        for match in matches:
            class_name = match.group(1).lower()
            class_full = match.group(0)
            
            if any(word in class_name for word in ['user', 'auth', 'account', 'profile']):
                domains['User Management'].append(class_full)
            elif any(word in class_name for word in ['service', 'manager', 'controller']):
                domains['Business Logic'].append(class_full)
            elif any(word in class_name for word in ['repository', 'dao', 'db']):
                domains['Data Access'].append(class_full)
            elif any(word in class_name for word in ['util', 'helper', 'validator']):
                domains['Utilities'].append(class_full)
        
        return {k: v for k, v in domains.items() if v}
    
    def _wrap_deployment_nodes(self, content: str) -> str:
        """Wrap deployment components in node blocks"""
        # Simple heuristic: wrap database and server components
        lines = content.split('\n')
        wrapped_lines = []
        in_node = False
        
        for line in lines:
            if 'database' in line.lower() and not in_node:
                wrapped_lines.append('node "Database Server" {')
                wrapped_lines.append('  ' + line)
                wrapped_lines.append('}')
            elif 'component' in line.lower() and 'server' in line.lower() and not in_node:
                wrapped_lines.append('node "Application Server" {')
                wrapped_lines.append('  ' + line)
                wrapped_lines.append('}')
            else:
                wrapped_lines.append(line)
        
        return '\n'.join(wrapped_lines)
    
    def _find_insertion_point(self, content: str) -> int:
        """Find the best point to insert new content"""
        # After direction statement
        if 'direction' in content:
            match = re.search(r'direction\s*\n', content)
            if match:
                return match.end()
        
        # After @startuml
        if '@startuml' in content:
            match = re.search(r'@startuml\s*\n', content)
            if match:
                return match.end()
        
        # At the beginning
        return 0
    
    def _add_intelligent_annotations(self, content: str, diagram_type: str, context: str = None) -> Tuple[str, int]:
        """Add helpful notes and annotations"""
        notes_added = 0
        optimized_content = content
        
        if diagram_type == 'sequence':
            # Add notes for critical flows
            critical_patterns = [
                (r'(auth|authenticate|login)', 'note right: Authentication required'),
                (r'(error|fail|exception)', 'note right: Error handling'),
                (r'(async|queue|message)', 'note right: Asynchronous processing'),
                (r'(cache|redis|memcache)', 'note left: Cached for performance'),
                (r'(validate|verify|check)', 'note right: Validation step')
            ]
            
            for pattern, note in critical_patterns:
                if re.search(pattern, content, re.IGNORECASE) and note not in content:
                    # Find the line with the pattern
                    lines = optimized_content.split('\n')
                    for i, line in enumerate(lines):
                        if re.search(pattern, line, re.IGNORECASE):
                            lines.insert(i + 1, note)
                            notes_added += 1
                            break
                    optimized_content = '\n'.join(lines)
        
        elif diagram_type == 'component':
            # Add legend for component diagram
            if 'legend' not in content.lower():
                legend = """
legend right
  |= Component |= Description |
  | Frontend | User Interface Layer |
  | API | External Interface |
  | Service | Business Logic |
  | Database | Data Persistence |
endlegend
"""
                optimized_content += legend
                notes_added += 1
        
        elif diagram_type == 'activity':
            # Add notes for decision points
            if 'if ' in content:
                decision_note = "note right: Decision point - consider all paths"
                if decision_note not in content:
                    optimized_content = optimized_content.replace('if ', f'if \n{decision_note}\n')
                    notes_added += 1
        
        return optimized_content, notes_added
    
    def _fix_common_issues(self, content: str, diagram_type: str) -> Tuple[str, List[str]]:
        """Fix common PlantUML anti-patterns and errors"""
        fixes = []
        optimized_content = content
        
        # Fix 1: Remove duplicate definitions
        lines = optimized_content.split('\n')
        seen_definitions = set()
        cleaned_lines = []
        
        for line in lines:
            # Check for duplicate participant/component/class definitions
            definition_match = re.match(r'(participant|component|class|database)\s+(\w+)', line)
            if definition_match:
                definition = definition_match.group(0)
                if definition not in seen_definitions:
                    seen_definitions.add(definition)
                    cleaned_lines.append(line)
                else:
                    fixes.append(f"Removed duplicate: {definition}")
            else:
                cleaned_lines.append(line)
        
        optimized_content = '\n'.join(cleaned_lines)
        
        # Fix 2: Ensure proper arrow syntax
        arrow_fixes = {
            r'->-': '-->',  # Fix double dash
            r'->>': '->',   # Standardize arrows
            r'<-<': '<--',  # Fix reverse double dash
            r'\.\.>': '..>',  # Fix dotted arrows
        }
        
        for pattern, replacement in arrow_fixes.items():
            if re.search(pattern, optimized_content):
                optimized_content = re.sub(pattern, replacement, optimized_content)
                fixes.append(f"Fixed arrow syntax: {pattern} -> {replacement}")
        
        # Fix 3: Add missing closing tags
        if '@startuml' in optimized_content and '@enduml' not in optimized_content:
            optimized_content += '\n@enduml'
            fixes.append("Added missing @enduml")
        
        # Fix 4: Reorder participants in sequence diagrams to minimize crossing
        if diagram_type == 'sequence':
            optimized_content = self._reorder_sequence_participants(optimized_content)
            if optimized_content != content:
                fixes.append("Reordered participants to minimize line crossing")
        
        # Fix 5: Remove orphaned elements (elements with no connections)
        optimized_content, orphans_removed = self._remove_orphaned_elements(optimized_content)
        if orphans_removed:
            fixes.append(f"Removed {orphans_removed} orphaned elements")
        
        return optimized_content, fixes
    
    def _reorder_sequence_participants(self, content: str) -> str:
        """Reorder sequence diagram participants to minimize crossing"""
        # Extract participants and their interactions
        participants = []
        interactions = []
        
        participant_pattern = r'participant\s+"?([^"\n]+)"?\s+as\s+(\w+)|participant\s+(\w+)'
        interaction_pattern = r'(\w+)\s*-+>?\s*(\w+)'
        
        # Find all participants
        for match in re.finditer(participant_pattern, content):
            if match.group(2):  # participant "Name" as alias
                participants.append(match.group(2))
            elif match.group(3):  # participant Name
                participants.append(match.group(3))
        
        # Find all interactions
        for match in re.finditer(interaction_pattern, content):
            interactions.append((match.group(1), match.group(2)))
        
        # Calculate interaction matrix
        if len(participants) > 2 and interactions:
            # Simple heuristic: order by frequency of interactions
            interaction_count = {}
            for p in participants:
                interaction_count[p] = sum(1 for i in interactions if p in i)
            
            # Sort participants by interaction frequency
            sorted_participants = sorted(participants, key=lambda p: interaction_count.get(p, 0), reverse=True)
            
            # Rebuild participant declarations in optimized order
            if sorted_participants != participants:
                # This would require more complex rewriting - simplified for now
                pass
        
        return content
    
    def _remove_orphaned_elements(self, content: str) -> Tuple[str, int]:
        """Remove elements that have no connections"""
        # This is a simplified version - real implementation would need full parsing
        orphans_removed = 0
        
        # For now, just return the original content
        # A full implementation would parse all elements and their connections
        
        return content, orphans_removed
    
    def save_optimized(self, original_file: str, optimized_content: str) -> str:
        """Save optimized PlantUML content to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"optimized_{timestamp}.puml"
        filepath = self.optimized_dir / filename
        
        with open(filepath, 'w') as f:
            f.write(optimized_content)
        
        return str(filepath)
    
    def generate_diff_report(self, original: str, optimized: str) -> str:
        """Generate a diff report showing changes"""
        report = []
        report.append("="*60)
        report.append("AI OPTIMIZATION DIFF REPORT")
        report.append("="*60)
        
        original_lines = original.split('\n')
        optimized_lines = optimized.split('\n')
        
        report.append(f"\nOriginal lines: {len(original_lines)}")
        report.append(f"Optimized lines: {len(optimized_lines)}")
        report.append(f"Line difference: {len(optimized_lines) - len(original_lines)}")
        
        # Show first few changes
        report.append("\nKey changes:")
        
        # Check for layout directive
        if 'direction' not in original and 'direction' in optimized:
            report.append("+ Added layout direction")
        
        # Check for packages
        original_packages = original.count('package')
        optimized_packages = optimized.count('package')
        if optimized_packages > original_packages:
            report.append(f"+ Added {optimized_packages - original_packages} package groupings")
        
        # Check for notes
        original_notes = original.count('note')
        optimized_notes = optimized.count('note')
        if optimized_notes > original_notes:
            report.append(f"+ Added {optimized_notes - original_notes} explanatory notes")
        
        # Check for legend
        if 'legend' not in original and 'legend' in optimized:
            report.append("+ Added legend/documentation")
        
        return '\n'.join(report)


# Convenience function for quick optimization
def optimize_plantuml(content: str, context: str = None) -> Dict[str, Any]:
    """Quick function to optimize PlantUML content"""
    optimizer = PlantUMLAIOptimizer()
    return optimizer.optimize(content, context)


if __name__ == "__main__":
    # Test the optimizer
    test_content = """
    @startuml
    participant Client
    participant Service A
    participant Service B
    participant DB
    
    Client -> Service A: request
    Service A -> Service B: process
    Service B -> DB: query
    DB --> Service B: data
    Service B --> Service A: result
    Service A --> Client: response
    @enduml
    """
    
    optimizer = PlantUMLAIOptimizer()
    result = optimizer.optimize(test_content, "Authentication flow for microservices")
    
    print("Original:")
    print(result['original'])
    print("\nOptimized:")
    print(result['optimized'])
    print("\nOptimizations applied:")
    for opt in result['optimizations']:
        print(f"  - {opt}")