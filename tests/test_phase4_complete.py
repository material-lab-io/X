#!/usr/bin/env python3
"""
Complete Phase 4 test with proper diagram setup
"""

import json
import shutil
from pathlib import Path

def setup_test_environment():
    """Setup test diagrams and threads"""
    
    # Create optimized directory
    opt_dir = Path("/home/kushagra/X/optimized")
    opt_dir.mkdir(exist_ok=True)
    
    # Copy existing diagrams with better names
    diagram_mappings = [
        ("automated_diagrams/png/docker-container-lifecycle-management.png", 
         "docker_lifecycle_opt.png"),
        ("automated_diagrams/png/microservices-communication-patterns.png",
         "microservices_communication_opt.png")
    ]
    
    for src, dst in diagram_mappings:
        src_path = Path(src)
        if src_path.exists():
            dst_path = opt_dir / dst
            shutil.copy(src_path, dst_path)
            print(f"✓ Copied {src} → {dst}")
    
    # Create test thread that matches our diagrams
    test_thread = {
        "topic": "Docker Container Lifecycle",
        "generatorType": "UnifiedGenerator",
        "generatedTweets": [
            "🐳 Understanding Docker container lifecycle is crucial for debugging and optimization. Let's explore!",
            "Docker containers have 5 main states: Created, Running, Paused, Stopped, and Removed. Each serves a purpose.",
            "Here's a visual representation of the Docker lifecycle states and transitions:\n\n📊 [Diagram Below]",
            "Pro tip: Use `docker ps -a` to see ALL containers, not just running ones. This helps track container history!",
            "What's your biggest Docker challenge? Let me know below! 👇"
        ]
    }
    
    # Save test thread
    with open("test_docker_lifecycle_thread.json", "w") as f:
        json.dump(test_thread, f, indent=2)
    
    print("\n✓ Created test thread: test_docker_lifecycle_thread.json")
    
    # Create another test thread
    microservices_thread = {
        "topic": "Microservices Communication Patterns",
        "generatorType": "UnifiedGenerator", 
        "generatedTweets": [
            "🔗 Let's explore how microservices communicate effectively in distributed systems!",
            "The main patterns are: Sync (REST/gRPC), Async (Message Queues), and Service Mesh. Each has tradeoffs.",
            "Here's how async communication flows between services:\n\n📈 [Architecture Diagram]",
            "Message queues provide decoupling and resilience but add complexity. Choose wisely!",
            "Which communication pattern do you prefer? Share your experience! 🤔"
        ]
    }
    
    with open("test_microservices_thread.json", "w") as f:
        json.dump(microservices_thread, f, indent=2)
    
    print("✓ Created test thread: test_microservices_thread.json")
    
    print(f"\n📁 Optimized diagrams directory: {opt_dir}")
    print("📝 Test threads created in current directory")
    
    return opt_dir


if __name__ == "__main__":
    print("🧪 Setting up Phase 4 test environment...")
    print("="*50)
    
    opt_dir = setup_test_environment()
    
    print("\n" + "="*50)
    print("✅ Test environment ready!")
    print("\nNow run:")
    print(f"  venv/bin/python tweet_diagram_binder.py test_docker_lifecycle_thread.json --dry-run")
    print("\nOr test both:")
    print(f"  venv/bin/python tweet_diagram_binder.py . --pattern 'test_*_thread.json' --dry-run")