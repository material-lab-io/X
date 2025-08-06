#!/usr/bin/env python3
"""
Phase 3: Automation Pipeline for Mermaid Diagram Processing
Extracts, renders, and tracks diagrams from thread outputs
"""

import json
import re
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import hashlib
import shutil


class DiagramAutomationPipeline:
    def __init__(self, base_dir: str = ".", output_dir: str = "diagrams"):
        """Initialize the automation pipeline"""
        self.base_dir = Path(base_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        self.mmd_dir = self.output_dir / "mmd"
        self.png_dir = self.output_dir / "png"
        self.metadata_dir = self.output_dir / "metadata"
        
        for dir in [self.mmd_dir, self.png_dir, self.metadata_dir]:
            dir.mkdir(exist_ok=True)
        
        # Check for mermaid CLI
        self.has_mmdc = self._check_mmdc()
        
        # Puppeteer config for mermaid CLI
        self.puppeteer_config = self.base_dir / "puppeteer-config.json"
        
    def _check_mmdc(self) -> bool:
        """Check if mermaid CLI is available"""
        try:
            result = subprocess.run(['which', 'mmdc'], capture_output=True)
            return result.returncode == 0
        except:
            return False
    
    def _create_topic_slug(self, topic: str) -> str:
        """Create a URL-friendly slug from topic"""
        # Convert to lowercase and replace spaces/special chars
        slug = topic.lower()
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        slug = re.sub(r'\s+', '-', slug)
        slug = re.sub(r'-+', '-', slug)
        slug = slug.strip('-')
        
        # Limit length
        if len(slug) > 50:
            slug = slug[:50].rsplit('-', 1)[0]
        
        return slug or 'untitled'
    
    def extract_mermaid_diagrams(self, content: str, topic: str = "") -> List[Dict]:
        """Extract all Mermaid diagrams from content"""
        diagrams = []
        
        # Pattern to match mermaid code blocks
        pattern = r'```mermaid\s*\n(.*?)```'
        matches = re.findall(pattern, content, re.DOTALL)
        
        for i, diagram_code in enumerate(matches):
            diagram_code = diagram_code.strip()
            
            # Generate unique ID for diagram
            diagram_hash = hashlib.md5(diagram_code.encode()).hexdigest()[:8]
            
            # Create filename
            topic_slug = self._create_topic_slug(topic)
            if len(matches) > 1:
                filename = f"{topic_slug}_{i+1}"
            else:
                filename = topic_slug
            
            diagrams.append({
                "code": diagram_code,
                "filename": filename,
                "hash": diagram_hash,
                "index": i
            })
        
        return diagrams
    
    def save_mermaid_file(self, diagram: Dict) -> str:
        """Save Mermaid code to .mmd file"""
        filepath = self.mmd_dir / f"{diagram['filename']}.mmd"
        
        # Avoid overwriting if content is different
        if filepath.exists():
            with open(filepath, 'r') as f:
                existing = f.read()
            if existing.strip() == diagram['code'].strip():
                return str(filepath)
            else:
                # Add hash to filename to avoid collision
                filepath = self.mmd_dir / f"{diagram['filename']}_{diagram['hash']}.mmd"
        
        with open(filepath, 'w') as f:
            f.write(diagram['code'])
        
        return str(filepath)
    
    def render_to_png(self, mmd_filepath: str) -> Optional[str]:
        """Render Mermaid diagram to PNG"""
        mmd_path = Path(mmd_filepath)
        png_filename = mmd_path.stem + '.png'
        png_filepath = self.png_dir / png_filename
        
        # Skip if already rendered
        if png_filepath.exists():
            return str(png_filepath)
        
        if not self.has_mmdc:
            print(f"Warning: mmdc not found. Cannot render {mmd_path.name}")
            return None
        
        try:
            # Prepare command
            cmd = [
                'mmdc',
                '-i', str(mmd_path),
                '-o', str(png_filepath),
                '-t', 'default',
                '-b', 'white'
            ]
            
            # Add puppeteer config if exists
            if self.puppeteer_config.exists():
                cmd.extend(['-p', str(self.puppeteer_config)])
            
            # Run mermaid CLI
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Rendered: {png_filename}")
                return str(png_filepath)
            else:
                print(f"❌ Render failed: {png_filename}")
                print(f"   Error: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"❌ Render error: {e}")
            return None
    
    def create_metadata(self, topic: str, diagrams: List[Dict], 
                       thread_data: Optional[Dict] = None) -> Dict:
        """Create metadata for processed diagrams"""
        metadata = {
            "topic": topic,
            "processed_at": datetime.utcnow().isoformat(),
            "diagram_count": len(diagrams),
            "diagrams": []
        }
        
        for diagram in diagrams:
            mmd_path = self.mmd_dir / f"{diagram['filename']}.mmd"
            png_path = self.png_dir / f"{diagram['filename']}.png"
            
            diagram_meta = {
                "filename": diagram['filename'],
                "hash": diagram['hash'],
                "mmd_path": str(mmd_path),
                "png_path": str(png_path) if png_path.exists() else None,
                "png_rendered": png_path.exists(),
                "code_length": len(diagram['code']),
                "diagram_type": self._detect_diagram_type(diagram['code'])
            }
            
            metadata["diagrams"].append(diagram_meta)
        
        # Add thread data if provided
        if thread_data:
            metadata["thread_info"] = {
                "tweet_count": len(thread_data.get("generatedTweets", [])),
                "template": thread_data.get("template"),
                "keywords": thread_data.get("keywords", [])[:5]
            }
        
        return metadata
    
    def _detect_diagram_type(self, code: str) -> str:
        """Detect the type of Mermaid diagram"""
        if 'graph TD' in code or 'graph TB' in code or 'graph LR' in code:
            return 'flowchart'
        elif 'sequenceDiagram' in code:
            return 'sequence'
        elif 'stateDiagram' in code:
            return 'state'
        elif 'classDiagram' in code:
            return 'class'
        elif 'gantt' in code:
            return 'gantt'
        else:
            return 'unknown'
    
    def save_metadata(self, metadata: Dict) -> str:
        """Save metadata to JSON file"""
        topic_slug = self._create_topic_slug(metadata['topic'])
        filepath = self.metadata_dir / f"{topic_slug}_metadata.json"
        
        with open(filepath, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return str(filepath)
    
    def process_thread_output(self, thread_json: Dict) -> Dict:
        """Process a complete thread output with diagrams"""
        topic = thread_json.get('topic', 'Untitled')
        results = {
            "topic": topic,
            "status": "success",
            "diagrams_extracted": 0,
            "diagrams_rendered": 0,
            "files": {
                "mmd": [],
                "png": [],
                "metadata": None
            }
        }
        
        try:
            # Check if diagram exists in thread data
            if 'diagram' in thread_json and thread_json['diagram']:
                diagram_info = thread_json['diagram']
                
                # Extract diagram from the code field
                diagrams = [{
                    "code": diagram_info['code'],
                    "filename": self._create_topic_slug(topic),
                    "hash": hashlib.md5(diagram_info['code'].encode()).hexdigest()[:8],
                    "index": 0
                }]
            else:
                # Extract from tweet content
                full_content = '\n\n'.join(thread_json.get('generatedTweets', []))
                diagrams = self.extract_mermaid_diagrams(full_content, topic)
            
            results["diagrams_extracted"] = len(diagrams)
            
            # Process each diagram
            for diagram in diagrams:
                # Save .mmd file
                mmd_path = self.save_mermaid_file(diagram)
                results["files"]["mmd"].append(mmd_path)
                
                # Render to PNG
                png_path = self.render_to_png(mmd_path)
                if png_path:
                    results["files"]["png"].append(png_path)
                    results["diagrams_rendered"] += 1
            
            # Create and save metadata
            metadata = self.create_metadata(topic, diagrams, thread_json)
            metadata_path = self.save_metadata(metadata)
            results["files"]["metadata"] = metadata_path
            
        except Exception as e:
            results["status"] = "error"
            results["error"] = str(e)
        
        return results
    
    def process_multiple_threads(self, thread_files: List[str]) -> List[Dict]:
        """Process multiple thread JSON files"""
        results = []
        
        for filepath in thread_files:
            print(f"\n📄 Processing: {filepath}")
            
            try:
                with open(filepath, 'r') as f:
                    thread_data = json.load(f)
                
                result = self.process_thread_output(thread_data)
                result["source_file"] = filepath
                results.append(result)
                
                print(f"   ✅ Extracted: {result['diagrams_extracted']} diagrams")
                print(f"   ✅ Rendered: {result['diagrams_rendered']} PNGs")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                results.append({
                    "source_file": filepath,
                    "status": "error",
                    "error": str(e)
                })
        
        return results
    
    def generate_index(self) -> str:
        """Generate an index of all processed diagrams"""
        index = {
            "generated_at": datetime.utcnow().isoformat(),
            "total_diagrams": 0,
            "total_rendered": 0,
            "topics": []
        }
        
        # Read all metadata files
        for metadata_file in self.metadata_dir.glob("*_metadata.json"):
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            topic_info = {
                "topic": metadata["topic"],
                "diagram_count": metadata["diagram_count"],
                "processed_at": metadata["processed_at"],
                "diagrams": []
            }
            
            for diagram in metadata["diagrams"]:
                topic_info["diagrams"].append({
                    "filename": diagram["filename"],
                    "type": diagram["diagram_type"],
                    "rendered": diagram["png_rendered"]
                })
                
                index["total_diagrams"] += 1
                if diagram["png_rendered"]:
                    index["total_rendered"] += 1
            
            index["topics"].append(topic_info)
        
        # Save index
        index_path = self.output_dir / "index.json"
        with open(index_path, 'w') as f:
            json.dump(index, f, indent=2)
        
        return str(index_path)


def main():
    """Command-line interface for the automation pipeline"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Process thread outputs for Mermaid diagrams")
    parser.add_argument("files", nargs="+", help="Thread JSON files to process")
    parser.add_argument("--output-dir", default="diagrams", help="Output directory")
    parser.add_argument("--no-render", action="store_true", help="Skip PNG rendering")
    parser.add_argument("--index", action="store_true", help="Generate index after processing")
    
    args = parser.parse_args()
    
    # Initialize pipeline
    pipeline = DiagramAutomationPipeline(output_dir=args.output_dir)
    
    if args.no_render:
        pipeline.has_mmdc = False
    
    # Process files
    print(f"🚀 Processing {len(args.files)} thread files...")
    results = pipeline.process_multiple_threads(args.files)
    
    # Summary
    print("\n📊 Summary:")
    successful = sum(1 for r in results if r["status"] == "success")
    total_extracted = sum(r.get("diagrams_extracted", 0) for r in results)
    total_rendered = sum(r.get("diagrams_rendered", 0) for r in results)
    
    print(f"   ✅ Successful: {successful}/{len(results)} files")
    print(f"   📝 Diagrams extracted: {total_extracted}")
    print(f"   🖼️  Diagrams rendered: {total_rendered}")
    
    # Generate index if requested
    if args.index:
        print("\n📚 Generating index...")
        index_path = pipeline.generate_index()
        print(f"   ✅ Index saved to: {index_path}")
    
    print(f"\n✨ Output directory: {pipeline.output_dir}")


if __name__ == "__main__":
    main()