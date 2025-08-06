#!/usr/bin/env python3
"""
Mermaid Diagram Generator for Twitter/X Technical Content
Generates clean, mobile-friendly technical diagrams
"""

import json
import re
from typing import Dict, List, Optional, Literal
from datetime import datetime
import subprocess
import base64
import requests
import os

DiagramType = Literal["architecture", "workflow", "sequence", "state"]

class MermaidDiagramGenerator:
    def __init__(self):
        """Initialize the Mermaid diagram generator"""
        self.templates = self._load_templates()
        self.render_method = self._detect_render_method()
        
    def _load_templates(self) -> Dict:
        """Load diagram templates"""
        return {
            "architecture": {
                "base": """%%{{init: {{'theme':'base', 'themeVariables': {{ 'primaryColor':'#1DA1F2'}}}}}}%%
graph TB
    %% Client Layer
    subgraph "Client Layer"
        {clients}
    end
    
    %% API Gateway
    GW[API Gateway]
    
    %% Service Layer
    subgraph "Services"
        {services}
    end
    
    %% Data Layer
    subgraph "Data"
        {storage}
    end
    
    %% Connections
    {connections}
    
    %% Styling
    classDef client fill:#E1F5FE,stroke:#01579B,stroke-width:2px
    classDef service fill:#FFF3E0,stroke:#E65100,stroke-width:2px
    classDef data fill:#F3E5F5,stroke:#4A148C,stroke-width:2px
    
    {styling}""",
                "node_limit": 10,
                "description": "System architecture with layers"
            },
            
            "workflow": {
                "base": """%%{{init: {{'theme':'neutral'}}}}%%
flowchart LR
    %% Start
    A((Start)) --> B{{{first_decision}}}
    
    %% Main Flow
    {main_flow}
    
    %% End States
    {end_states}
    
    %% Styling
    style A fill:#4CAF50,color:#fff
    {custom_styles}""",
                "node_limit": 8,
                "description": "Process workflow with decision points"
            },
            
            "sequence": {
                "base": """sequenceDiagram
    participant U as User
    participant S as System
    participant D as Database
    
    {interactions}
    
    Note over S: {processing_note}""",
                "node_limit": 15,
                "description": "API or interaction sequence"
            },
            
            "state": {
                "base": """stateDiagram-v2
    [*] --> {initial_state}
    
    {state_transitions}
    
    {final_state} --> [*]
    
    note right of {key_state}: {note}""",
                "node_limit": 8,
                "description": "State machine for agents"
            }
        }
    
    def _detect_render_method(self) -> str:
        """Detect available rendering method"""
        # Check if mermaid CLI is installed
        try:
            result = subprocess.run(['mmdc', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return "cli"
        except:
            pass
        
        # Fall back to web API
        return "api"
    
    def generate_architecture_diagram(self, components: Dict) -> str:
        """Generate system architecture diagram"""
        template = self.templates["architecture"]["base"]
        
        # Build client nodes
        clients = []
        for i, client in enumerate(components.get("clients", ["Web", "Mobile", "CLI"])):
            clients.append(f"C{i}[{client}]")
        
        # Build service nodes
        services = []
        for i, service in enumerate(components.get("services", ["Auth", "Core", "ML"])):
            services.append(f"S{i}[{service}]")
        
        # Build storage nodes
        storage = []
        for i, store in enumerate(components.get("storage", ["Database", "Cache"])):
            if "database" in store.lower() or "db" in store.lower():
                storage.append(f"D{i}[({store})]")
            else:
                storage.append(f"D{i}[{store}]")
        
        # Build connections
        connections = []
        # Clients to gateway
        for i in range(len(clients)):
            connections.append(f"C{i} --> GW")
        # Gateway to services
        for i in range(len(services)):
            connections.append(f"GW --> S{i}")
        # Services to storage (simplified)
        if services and storage:
            connections.append(f"S0 --> D0")
            if len(services) > 1 and len(storage) > 1:
                connections.append(f"S1 --> D1")
        
        # Build styling
        styling = []
        styling.extend([f"class C{i} client" for i in range(len(clients))])
        styling.extend([f"class S{i} service" for i in range(len(services))])
        styling.extend([f"class D{i} data" for i in range(len(storage))])
        
        # Replace template variables
        diagram = template.format(
            clients="\n        ".join(clients),
            services="\n        ".join(services),
            storage="\n        ".join(storage),
            connections="\n    ".join(connections),
            styling="\n    ".join(styling)
        )
        
        return self._clean_diagram(diagram)
    
    def generate_workflow_diagram(self, workflow: Dict) -> str:
        """Generate process workflow diagram"""
        template = self.templates["workflow"]["base"]
        
        steps = workflow.get("steps", [])
        if not steps:
            steps = ["Validate", "Process", "Transform", "Store"]
        
        # Limit steps for readability
        steps = steps[:6]
        
        # Build main flow
        main_flow = []
        node_id = ord('B')  # Start from B (A is Start)
        
        for i, step in enumerate(steps):
            current = chr(node_id + i)
            next_node = chr(node_id + i + 1) if i < len(steps) - 1 else 'END'
            
            if "?" in step:  # Decision node
                main_flow.append(f"{current}{{{step}}}")
                main_flow.append(f"{current} -->|Yes| {next_node}")
                main_flow.append(f"{current} -->|No| ERR[Handle Error]")
            else:  # Process node
                main_flow.append(f"{current}[{step}]")
                if next_node != 'END':
                    main_flow.append(f"{current} --> {next_node}")
                else:
                    main_flow.append(f"{current} --> SUCCESS((Success))")
        
        # End states
        end_states = ["SUCCESS((Success))", "ERR --> FAIL((Failed))"]
        
        # Custom styles
        custom_styles = [
            "style SUCCESS fill:#4CAF50,color:#fff",
            "style FAIL fill:#F44336,color:#fff",
            "style ERR fill:#FF9800,color:#fff"
        ]
        
        # Build diagram
        first_decision = workflow.get("first_decision", "Valid Input?")
        diagram = template.format(
            first_decision=first_decision,
            main_flow="\n    ".join(main_flow),
            end_states="\n    ".join(end_states),
            custom_styles="\n    ".join(custom_styles)
        )
        
        return self._clean_diagram(diagram)
    
    def generate_sequence_diagram(self, interactions: List[Dict]) -> str:
        """Generate sequence diagram for API/system interactions"""
        template = self.templates["sequence"]["base"]
        
        if not interactions:
            # Default example
            interactions = [
                {"from": "U", "to": "S", "message": "Request Data"},
                {"from": "S", "to": "D", "message": "Query"},
                {"from": "D", "to": "S", "message": "Results"},
                {"from": "S", "to": "U", "message": "Response"}
            ]
        
        # Build interaction strings
        interaction_strs = []
        for interaction in interactions[:10]:  # Limit for readability
            from_p = interaction.get("from", "U")
            to_p = interaction.get("to", "S")
            message = interaction.get("message", "Data")
            arrow = "->>" if interaction.get("async", False) else "->>"
            
            interaction_strs.append(f"{from_p}{arrow}{to_p}: {message}")
        
        # Add activation if needed
        if len(interactions) > 2:
            interaction_strs.insert(1, "activate S")
            interaction_strs.append("deactivate S")
        
        diagram = template.format(
            interactions="\n    ".join(interaction_strs),
            processing_note="Processing logic here"
        )
        
        return self._clean_diagram(diagram)
    
    def generate_state_diagram(self, states: Dict) -> str:
        """Generate state diagram for agent behavior"""
        template = self.templates["state"]["base"]
        
        initial = states.get("initial", "Idle")
        final = states.get("final", "Complete")
        transitions = states.get("transitions", [])
        
        if not transitions:
            # Default example
            transitions = [
                {"from": "Idle", "to": "Processing", "label": "Start"},
                {"from": "Processing", "to": "Validating", "label": "Data Ready"},
                {"from": "Validating", "to": "Complete", "label": "Valid"},
                {"from": "Validating", "to": "Error", "label": "Invalid"},
                {"from": "Error", "to": "Idle", "label": "Reset"}
            ]
        
        # Build transition strings
        transition_strs = []
        key_state = initial
        
        for trans in transitions[:8]:  # Limit for readability
            from_state = trans.get("from", "State1")
            to_state = trans.get("to", "State2") 
            label = trans.get("label", "")
            
            if label:
                transition_strs.append(f"{from_state} --> {to_state}: {label}")
            else:
                transition_strs.append(f"{from_state} --> {to_state}")
            
            # Track a key state for the note
            if "process" in to_state.lower():
                key_state = to_state
        
        diagram = template.format(
            initial_state=initial,
            state_transitions="\n    ".join(transition_strs),
            final_state=final,
            key_state=key_state,
            note="Critical state"
        )
        
        return self._clean_diagram(diagram)
    
    def _clean_diagram(self, diagram: str) -> str:
        """Clean and validate diagram syntax"""
        # Remove empty lines but preserve structure
        lines = [line for line in diagram.split('\n') if line.strip()]
        
        # Join with proper newlines
        cleaned = '\n'.join(lines)
        
        # Remove excessive spaces within lines (but not newlines)
        lines = cleaned.split('\n')
        cleaned_lines = []
        for line in lines:
            # Preserve indentation but remove double spaces
            line = re.sub(r'  +', ' ', line)
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines).strip()
    
    def render_diagram(self, diagram_code: str, output_path: str, 
                      theme: str = "default", bg_color: str = "white") -> bool:
        """Render Mermaid diagram to PNG"""
        if self.render_method == "cli":
            return self._render_with_cli(diagram_code, output_path, theme, bg_color)
        else:
            return self._render_with_api(diagram_code, output_path)
    
    def _render_with_cli(self, diagram_code: str, output_path: str,
                        theme: str, bg_color: str) -> bool:
        """Render using mermaid CLI"""
        try:
            # Write diagram to temp file
            temp_file = "/tmp/temp_diagram.mmd"
            with open(temp_file, 'w') as f:
                f.write(diagram_code)
            
            # Run mermaid CLI with puppeteer config for sandbox issues
            puppeteer_config = os.path.join(os.path.dirname(__file__), 'puppeteer-config.json')
            cmd = [
                'mmdc',
                '-i', temp_file,
                '-o', output_path,
                '-t', theme,
                '-b', bg_color,
                '-p', puppeteer_config  # Use puppeteer config
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Clean up temp file
            os.remove(temp_file)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"CLI render error: {e}")
            return False
    
    def _render_with_api(self, diagram_code: str, output_path: str) -> bool:
        """Render using Kroki.io API"""
        try:
            # Encode diagram
            encoded = base64.urlsafe_b64encode(
                diagram_code.encode('utf-8')
            ).decode('ascii').rstrip('=')
            
            # Call Kroki API
            url = f"https://kroki.io/mermaid/png/{encoded}"
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                return True
            else:
                print(f"API render error: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"API render error: {e}")
            return False
    
    def generate_diagram_explanation(self, topic: str, diagram_type: str, 
                                    diagram_code: str) -> str:
        """Generate explanation for the diagram"""
        explanations = {
            "architecture": f"This flowchart visualizes the {topic} architecture, showing the hierarchical relationship between client interfaces, service layers, and data storage components. The color coding highlights different architectural layers: blue for client-facing components, orange for core services, and purple for data persistence layers.",
            
            "workflow": f"This diagram illustrates the {topic} workflow, mapping the sequential process from initiation to completion. Decision points (diamonds) show where the flow branches based on conditions, while colored nodes indicate critical stages: green for successful paths and red for error handling or optimization triggers.",
            
            "sequence": f"This sequence diagram demonstrates the interaction flow for {topic}, showing how different components communicate over time. Each arrow represents a message or API call, with the vertical timeline indicating the order of operations and system responses.",
            
            "state": f"This state diagram models the behavior lifecycle for {topic}, tracking transitions between different operational states. The diagram shows how the system responds to various events, with colored states highlighting critical phases: initial setup (blue), active processing (green), and error recovery (red)."
        }
        
        return explanations.get(diagram_type, 
            f"This diagram provides a visual representation of {topic}, illustrating key components and their relationships.")
    
    def recommend_tweet_placement(self, diagram_type: str, context: Optional[Dict]) -> Dict:
        """Recommend where to place the diagram in the thread"""
        recommendations = {
            "architecture": {
                "tweet_number": 3,
                "reasoning": "Place after introducing the concept and before diving into implementation details",
                "placeholder": "📊 [Flowchart Attached Below]"
            },
            "workflow": {
                "tweet_number": 4,
                "reasoning": "Insert after explaining the problem and initial steps, before discussing optimizations",
                "placeholder": "📊 [Flowchart Attached Below]"
            },
            "sequence": {
                "tweet_number": 3,
                "reasoning": "Show after describing the components but before detailed interaction analysis",
                "placeholder": "📊 [Flowchart Attached Below]"
            },
            "state": {
                "tweet_number": 4,
                "reasoning": "Place after explaining the concept and states, before discussing transitions",
                "placeholder": "📊 [Flowchart Attached Below]"
            }
        }
        
        return recommendations.get(diagram_type, {
            "tweet_number": 3,
            "reasoning": "Place after core concept introduction for visual reinforcement",
            "placeholder": "📊 [Flowchart Attached Below]"
        })
    
    def generate_diagram_for_topic(self, topic: str, diagram_type: DiagramType,
                                  context: Optional[Dict] = None) -> Dict:
        """Generate appropriate diagram based on topic"""
        context = context or {}
        
        # Topic-specific diagram generation
        if "docker" in topic.lower():
            if diagram_type == "architecture":
                components = {
                    "clients": ["Docker CLI", "Docker Desktop"],
                    "services": ["Docker Daemon", "Container Runtime", "Image Registry"],
                    "storage": ["Image Cache", "Container Storage"]
                }
                diagram_code = self.generate_architecture_diagram(components)
            else:
                workflow = {
                    "steps": ["Pull Image", "Create Container", "Start Process", 
                             "Monitor Health", "Stop Container"],
                    "first_decision": "Image Exists?"
                }
                diagram_code = self.generate_workflow_diagram(workflow)
                
        elif "agent" in topic.lower() or "ai" in topic.lower():
            if diagram_type == "state":
                states = {
                    "initial": "Idle",
                    "final": "TaskComplete",
                    "transitions": [
                        {"from": "Idle", "to": "ReceiveTask", "label": "New Task"},
                        {"from": "ReceiveTask", "to": "Planning", "label": "Valid"},
                        {"from": "Planning", "to": "Executing", "label": "Plan Ready"},
                        {"from": "Executing", "to": "Monitoring", "label": "Started"},
                        {"from": "Monitoring", "to": "TaskComplete", "label": "Success"},
                        {"from": "Monitoring", "to": "ErrorHandling", "label": "Failed"},
                        {"from": "ErrorHandling", "to": "Planning", "label": "Retry"}
                    ]
                }
                diagram_code = self.generate_state_diagram(states)
            else:
                components = {
                    "clients": ["User Interface", "API Client"],
                    "services": ["Agent Core", "LLM Service", "Tool Manager"],
                    "storage": ["Context Store", "Knowledge Base"]
                }
                diagram_code = self.generate_architecture_diagram(components)
                
        else:
            # Generic diagram based on type
            if diagram_type == "architecture":
                diagram_code = self.generate_architecture_diagram(context)
            elif diagram_type == "workflow":
                diagram_code = self.generate_workflow_diagram(context)
            elif diagram_type == "sequence":
                diagram_code = self.generate_sequence_diagram(
                    context.get("interactions", [])
                )
            else:
                diagram_code = self.generate_state_diagram(context)
        
        # Generate explanation and placement recommendation
        explanation = self.generate_diagram_explanation(topic, diagram_type, diagram_code)
        placement = self.recommend_tweet_placement(diagram_type, context)
        
        return {
            "diagram_code": diagram_code,
            "diagram_type": diagram_type,
            "explanation": explanation,
            "placement_recommendation": placement,
            "render_method": self.render_method,
            "timestamp": datetime.utcnow().isoformat()
        }


def main():
    """Test the diagram generator"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate Mermaid diagrams")
    parser.add_argument("topic", help="Topic for the diagram")
    parser.add_argument("--type", choices=["architecture", "workflow", "sequence", "state"],
                       default="architecture", help="Diagram type")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--render", action="store_true", help="Render to PNG")
    
    args = parser.parse_args()
    
    generator = MermaidDiagramGenerator()
    
    # Generate diagram
    result = generator.generate_diagram_for_topic(args.topic, args.type)
    
    print("Generated Mermaid Diagram:")
    print("=" * 50)
    print(result["diagram_code"])
    print("=" * 50)
    
    # Save or render if requested
    if args.output:
        if args.render:
            # Render to PNG
            png_path = args.output.replace('.mmd', '.png')
            if generator.render_diagram(result["diagram_code"], png_path):
                print(f"Rendered to: {png_path}")
            else:
                print("Rendering failed, saving code instead")
                with open(args.output, 'w') as f:
                    f.write(result["diagram_code"])
        else:
            # Save code
            with open(args.output, 'w') as f:
                f.write(result["diagram_code"])
            print(f"Saved to: {args.output}")


if __name__ == "__main__":
    main()