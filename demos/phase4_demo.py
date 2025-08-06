#!/usr/bin/env python3
"""
Phase 4 Demo: Complete Tweet + Diagram Binding Pipeline

This script demonstrates the full workflow from thread generation
to posting with properly positioned media.
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_sample_diagrams():
    """Create sample optimized diagrams for testing"""
    optimized_dir = Path("/home/kushagra/X/optimized")
    optimized_dir.mkdir(exist_ok=True)
    
    # Sample Mermaid diagrams
    diagrams = {
        "docker_architecture": """graph TD
    A[Docker Client] --> B[Docker Daemon]
    B --> C[Container Runtime]
    B --> D[Image Registry]
    C --> E[Container 1]
    C --> F[Container 2]
    
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#bbf,stroke:#333,stroke-width:2px""",
        
        "microservices_flow": """graph LR
    A[API Gateway] --> B[Auth Service]
    A --> C[User Service]
    A --> D[Order Service]
    D --> E[Payment Service]
    D --> F[Inventory Service]
    
    style A fill:#f96,stroke:#333,stroke-width:2px"""
    }
    
    logger.info("Creating sample diagrams...")
    
    for name, mermaid_code in diagrams.items():
        # Save Mermaid file
        mmd_file = optimized_dir / f"{name}.mmd"
        with open(mmd_file, 'w') as f:
            f.write(mermaid_code)
        
        # Render to PNG (if mmdc available)
        png_file = optimized_dir / f"{name}_opt.png"
        try:
            subprocess.run([
                "mmdc", "-i", str(mmd_file), "-o", str(png_file),
                "-p", "puppeteer-config.json"
            ], check=True, capture_output=True)
            logger.info(f"✓ Created: {png_file.name}")
        except Exception as e:
            logger.warning(f"Could not render {name}: {e}")
            # Create placeholder
            Path(png_file).touch()
    
    return optimized_dir


def create_sample_threads():
    """Create sample thread JSON files for testing"""
    threads = [
        {
            "topic": "Docker Architecture Deep Dive",
            "generatorType": "UnifiedGenerator",
            "template": "ConceptualDeepDive",
            "contentType": "Thread",
            "generatedTweets": [
                "🐳 Let's dive deep into Docker architecture! Understanding how Docker works under the hood will level up your containerization game.",
                "Docker uses a client-server architecture. The Docker client talks to the Docker daemon, which does the heavy lifting of building, running, and distributing containers.",
                "Here's a visual breakdown of the Docker architecture:\n\n📊 [Architecture Diagram Below]",
                "The Docker daemon manages Docker objects like images, containers, networks, and volumes. It can also communicate with other daemons to manage Docker services.",
                "Pro tip: Use 'docker system df' to see how much space Docker is using on your system. Clean up with 'docker system prune' regularly! 🧹",
                "What's your favorite Docker feature? Let me know below! 👇"
            ],
            "diagram": {
                "type": "architecture",
                "placement": {"tweet_number": 3}
            }
        },
        {
            "topic": "Microservices Communication Patterns",
            "generatorType": "UnifiedGenerator", 
            "template": "TechnicalBreakdown",
            "contentType": "Thread",
            "generatedTweets": [
                "🔗 Microservices communication is crucial for distributed systems. Let's explore the main patterns!",
                "1️⃣ Synchronous: REST APIs and gRPC. Direct, request-response communication. Great for real-time needs but creates coupling.",
                "2️⃣ Asynchronous: Message queues (RabbitMQ, Kafka). Decoupled, scalable, but adds complexity. Here's how it flows: 📈",
                "3️⃣ Service Mesh: Istio/Linkerd handle communication, security, and observability. Takes the burden off your services!",
                "Choose based on your needs: REST for simplicity, gRPC for performance, async for scalability. What pattern do you prefer?"
            ]
        }
    ]
    
    logger.info("Creating sample thread files...")
    
    thread_files = []
    for thread in threads:
        filename = f"sample_thread_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{thread['topic'][:20].replace(' ', '_')}.json"
        filepath = Path(filename)
        
        with open(filepath, 'w') as f:
            json.dump(thread, f, indent=2)
        
        logger.info(f"✓ Created: {filename}")
        thread_files.append(filepath)
    
    return thread_files


def run_phase4_demo():
    """Run the complete Phase 4 demonstration"""
    print("\n🚀 Phase 4 Demo: Tweet + Diagram Binding Pipeline")
    print("="*60)
    
    # Step 1: Create sample diagrams
    print("\n📸 Step 1: Creating sample diagrams...")
    diagram_dir = create_sample_diagrams()
    
    # Step 2: Create sample threads
    print("\n📝 Step 2: Creating sample threads...")
    thread_files = create_sample_threads()
    
    # Step 3: Run binding in dry-run mode
    print("\n🔗 Step 3: Testing tweet-diagram binding...")
    
    for thread_file in thread_files:
        print(f"\n--- Processing: {thread_file} ---")
        
        # Run the binder in dry-run mode
        cmd = [
            sys.executable,
            "tweet_diagram_binder.py",
            str(thread_file),
            "--dry-run",
            "--diagram-dir", str(diagram_dir)
        ]
        
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to process {thread_file}: {e}")
    
    print("\n✅ Phase 4 Demo Complete!")
    print("\nNext steps:")
    print("1. Set your Twitter API credentials:")
    print("   export API_KEY='your_key'")
    print("   export API_SECRET='your_secret'")
    print("   export ACCESS_TOKEN='your_token'")
    print("   export ACCESS_TOKEN_SECRET='your_token_secret'")
    print("\n2. Run without --dry-run to actually post:")
    print(f"   python tweet_diagram_binder.py {thread_files[0]}")
    print("\n3. Or process all threads:")
    print("   python tweet_diagram_binder.py . --pattern 'sample_thread_*.json'")


if __name__ == "__main__":
    run_phase4_demo()