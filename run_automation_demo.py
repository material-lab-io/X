#!/usr/bin/env python3
"""
Demo script to showcase the complete Phase 3 automation pipeline
"""

import json
import os
from diagram_automation_pipeline import DiagramAutomationPipeline


def create_sample_thread_with_diagram():
    """Create a sample thread output with embedded Mermaid diagram"""
    thread_data = {
        "topic": "Docker Container Lifecycle Management",
        "generatorType": "StyleAware",
        "template": "ConceptualDeepDive",
        "contentType": "Thread",
        "generatedTweets": [
            "1/6 Ever wondered what happens inside Docker when you run a container? 🐳 Let's dive deep into the container lifecycle!",
            "2/6 Docker containers go through distinct states: Created → Running → Paused → Stopped → Removed. Each transition is managed by the Docker daemon.",
            "3/6 Here's how it works visually:\n\n📊 [Flowchart Attached Below]",
            "4/6 The `docker run` command does THREE things: 1) Creates container from image 2) Allocates resources 3) Starts the process. Magic! ✨",
            "5/6 Pro tip: Use `docker ps -a` to see ALL containers (including stopped). Many devs miss this and wonder where their containers went! 🔍",
            "6/6 Understanding lifecycle = better debugging. Next time a container acts weird, check its state first! What's your biggest Docker challenge? 💬"
        ],
        "diagram": {
            "type": "state",
            "code": """stateDiagram-v2
    [*] --> Created: docker create
    Created --> Running: docker start
    Running --> Paused: docker pause
    Paused --> Running: docker unpause
    Running --> Stopped: docker stop
    Stopped --> Running: docker restart
    Stopped --> Removed: docker rm
    Running --> Removed: docker rm -f
    Removed --> [*]
    
    note right of Running: Container actively executing
    note right of Paused: Processes suspended
    note right of Stopped: Process terminated, filesystem preserved""",
            "explanation": "This state diagram shows the complete Docker container lifecycle, from creation to removal. Each arrow represents a Docker command that transitions the container between states.",
            "placement": {
                "tweet_number": 3,
                "reasoning": "Placed after introducing the concept of container states"
            }
        }
    }
    
    # Save sample thread
    with open('sample_thread_docker.json', 'w') as f:
        json.dump(thread_data, f, indent=2)
    
    return 'sample_thread_docker.json'


def create_sample_thread_with_inline_mermaid():
    """Create a thread with Mermaid code in tweet content"""
    thread_data = {
        "topic": "Microservices Communication Patterns",
        "generatorType": "StyleAware",
        "template": "WorkflowShare",
        "contentType": "Thread",
        "generatedTweets": [
            "1/5 Microservices talking to each other? Here are the 3 patterns you NEED to know! 🎯",
            "2/5 Pattern 1: Synchronous HTTP/REST - Simple but creates coupling. Good for real-time needs.",
            "3/5 Pattern 2: Message Queues - Async & resilient! Here's the flow:\n\n```mermaid\ngraph LR\n    A[Service A] -->|Publish| Q[Message Queue]\n    Q -->|Subscribe| B[Service B]\n    Q -->|Subscribe| C[Service C]\n    style Q fill:#f9f,stroke:#333,stroke-width:4px\n```",
            "4/5 Pattern 3: Event Streaming - Best for high-volume data. Think Kafka, Pulsar.",
            "5/5 Pro tip: Start simple (HTTP), evolve to queues when you need resilience. What pattern do you use? 🤔"
        ]
    }
    
    with open('sample_thread_microservices.json', 'w') as f:
        json.dump(thread_data, f, indent=2)
    
    return 'sample_thread_microservices.json'


def run_demo():
    """Run the complete automation pipeline demo"""
    print("🚀 Phase 3 Automation Pipeline Demo")
    print("=" * 50)
    
    # Step 1: Create sample files
    print("\n📝 Step 1: Creating sample thread outputs...")
    file1 = create_sample_thread_with_diagram()
    file2 = create_sample_thread_with_inline_mermaid()
    print(f"   ✅ Created: {file1}")
    print(f"   ✅ Created: {file2}")
    
    # Step 2: Initialize pipeline
    print("\n🔧 Step 2: Initializing automation pipeline...")
    pipeline = DiagramAutomationPipeline(output_dir="automated_diagrams")
    print(f"   ✅ Output directory: {pipeline.output_dir}")
    print(f"   ✅ Mermaid CLI available: {pipeline.has_mmdc}")
    
    # Step 3: Process threads
    print("\n⚙️ Step 3: Processing thread outputs...")
    results = pipeline.process_multiple_threads([file1, file2])
    
    # Step 4: Generate index
    print("\n📚 Step 4: Generating diagram index...")
    index_path = pipeline.generate_index()
    print(f"   ✅ Index created: {index_path}")
    
    # Step 5: Display results
    print("\n📊 Results Summary:")
    print("-" * 50)
    
    for result in results:
        print(f"\n📄 {result['source_file']}:")
        print(f"   Topic: {result['topic']}")
        print(f"   Status: {result['status']}")
        print(f"   Diagrams extracted: {result['diagrams_extracted']}")
        print(f"   Diagrams rendered: {result['diagrams_rendered']}")
        
        if result['files']['mmd']:
            print("   📝 MMD files:")
            for mmd in result['files']['mmd']:
                print(f"      - {mmd}")
        
        if result['files']['png']:
            print("   🖼️ PNG files:")
            for png in result['files']['png']:
                print(f"      - {png}")
    
    # Step 6: Show directory structure
    print("\n📁 Generated Directory Structure:")
    print("-" * 50)
    
    for root, dirs, files in os.walk(pipeline.output_dir):
        level = root.replace(str(pipeline.output_dir), '').count(os.sep)
        indent = ' ' * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = ' ' * 2 * (level + 1)
        for file in files:
            print(f"{subindent}{file}")
    
    print("\n✨ Demo complete! Check the 'automated_diagrams' directory.")


if __name__ == "__main__":
    run_demo()