#!/usr/bin/env python3
"""
Phase 4: Tweet + Diagram Binding and Publishing

This module handles the final preparation and posting of threads with
properly positioned media attachments.
"""

import json
import os
import sys
import re
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import argparse
from difflib import SequenceMatcher

try:
    from twitter_publisher import TwitterPublisher
except ImportError:
    # Twitter publisher not available, but we can still do dry runs
    TwitterPublisher = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TweetDiagramBinder:
    """Binds tweets with their corresponding diagrams for publishing"""
    
    def __init__(self, diagram_dir: str = "/home/kushagra/X/optimized"):
        """
        Initialize the binder with diagram directory
        
        Args:
            diagram_dir: Directory containing optimized diagram PNGs
        """
        self.diagram_dir = Path(diagram_dir)
        self.publisher = None  # Lazy initialization
        
        # Scan available diagrams
        self.available_diagrams = self._scan_diagrams()
        logger.info(f"Found {len(self.available_diagrams)} diagrams in {self.diagram_dir}")
    
    def _scan_diagrams(self) -> Dict[str, Path]:
        """Scan and index available diagram files"""
        diagrams = {}
        
        if not self.diagram_dir.exists():
            logger.warning(f"Diagram directory not found: {self.diagram_dir}")
            return diagrams
        
        # Scan for PNG files
        for png_file in self.diagram_dir.glob("*.png"):
            # Extract base name for matching
            base_name = png_file.stem.replace("_optimized", "").replace("_opt", "")
            diagrams[base_name.lower()] = png_file
            
        return diagrams
    
    def _find_best_diagram_match(self, topic: str, tweet_content: str) -> Optional[Path]:
        """
        Find the best matching diagram for a topic/tweet
        
        Args:
            topic: Thread topic
            tweet_content: Tweet text that might contain diagram reference
            
        Returns:
            Path to best matching diagram or None
        """
        # Extract keywords from topic and tweet
        keywords = self._extract_keywords(topic + " " + tweet_content)
        
        logger.debug(f"Keywords extracted: {keywords}")
        logger.debug(f"Available diagrams: {list(self.available_diagrams.keys())}")
        
        best_match = None
        best_score = 0.0
        
        for diagram_key, diagram_path in self.available_diagrams.items():
            # Calculate similarity score
            score = self._calculate_similarity(keywords, diagram_key)
            logger.debug(f"Score for {diagram_key}: {score:.3f}")
            
            if score > best_score:
                best_score = score
                best_match = diagram_path
        
        # Only return if score is above threshold
        if best_score > 0.3:
            logger.info(f"Best diagram match for '{topic}': {best_match.name} (score: {best_score:.2f})")
            return best_match
        
        logger.warning(f"No suitable diagram found for topic: {topic} (best score: {best_score:.3f})")
        return None
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract relevant keywords from text for matching"""
        # Convert to lowercase and remove special characters
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Common words to ignore
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 
                      'to', 'for', 'of', 'with', 'by', 'from', 'is', 'are',
                      'was', 'were', 'been', 'be', 'have', 'has', 'had',
                      'do', 'does', 'did', 'will', 'would', 'could', 'should'}
        
        # Extract meaningful words
        words = [w for w in text.split() if w and w not in stop_words]
        
        return words
    
    def _calculate_similarity(self, keywords: List[str], diagram_name: str) -> float:
        """Calculate similarity score between keywords and diagram name"""
        diagram_words = self._extract_keywords(diagram_name)
        
        if not keywords or not diagram_words:
            return 0.0
        
        # Check for exact matches
        exact_matches = sum(1 for kw in keywords if kw in diagram_words)
        
        # Check for partial matches using sequence matcher
        partial_score = 0.0
        for kw in keywords:
            for dw in diagram_words:
                ratio = SequenceMatcher(None, kw, dw).ratio()
                if ratio > 0.8:  # High similarity threshold
                    partial_score += ratio
        
        # Check if diagram name contains any keyword as substring
        substring_matches = sum(1 for kw in keywords if kw in diagram_name.lower())
        
        # Combined score (weighted)
        total_matches = exact_matches + partial_score * 0.5 + substring_matches * 0.3
        total_score = total_matches / max(len(keywords), 1)
        
        return min(total_score, 1.0)  # Cap at 1.0
    
    def _identify_diagram_tweet(self, tweets: List[str], diagram_info: Optional[Dict] = None) -> int:
        """
        Identify which tweet should have the diagram attached
        
        Args:
            tweets: List of tweet texts
            diagram_info: Optional diagram placement info from generation
            
        Returns:
            Index of tweet to attach diagram to (0-based)
        """
        # If diagram info provided, use it
        if diagram_info and 'placement' in diagram_info:
            placement = diagram_info['placement']
            if 'tweet_number' in placement:
                # Convert 1-based to 0-based index
                return placement['tweet_number'] - 1
        
        # Otherwise, look for diagram indicators
        diagram_indicators = [
            'diagram', 'flowchart', 'chart', 'visual', 'attached',
            'below', 'above', 'following', '📊', '📈', '📉', '🔍'
        ]
        
        for i, tweet in enumerate(tweets):
            tweet_lower = tweet.lower()
            if any(indicator in tweet_lower for indicator in diagram_indicators):
                logger.info(f"Found diagram indicator in tweet {i+1}")
                return i
        
        # Default to second tweet (first is usually intro)
        if len(tweets) > 1:
            return 1
        
        return 0
    
    def prepare_thread_with_media(self, thread_data: Dict, dry_run: bool = False) -> List[Dict]:
        """
        Prepare thread data with appropriate media attachments
        
        Args:
            thread_data: Thread JSON data
            dry_run: If True, don't actually prepare media
            
        Returns:
            List of tweet dictionaries with text and image_path
        """
        topic = thread_data.get('topic', 'Unknown')
        
        # Handle different JSON formats
        if 'generatedTweets' in thread_data:
            tweets = thread_data['generatedTweets']
        elif 'tweets' in thread_data:
            tweets = thread_data['tweets']
        else:
            raise ValueError("No tweets found in thread data")
        
        # Get diagram info if available
        diagram_info = thread_data.get('diagram')
        
        # Find best matching diagram
        diagram_path = None
        if diagram_info and 'code' in diagram_info:
            # Thread has diagram info, find matching file
            diagram_path = self._find_best_diagram_match(topic, str(diagram_info))
        else:
            # No diagram info, try to match based on topic
            diagram_path = self._find_best_diagram_match(topic, " ".join(tweets[:2]))
        
        # Identify which tweet gets the diagram
        diagram_tweet_idx = self._identify_diagram_tweet(tweets, diagram_info)
        
        # Prepare tweet list
        prepared_tweets = []
        for i, tweet_text in enumerate(tweets):
            tweet_dict = {'text': tweet_text}
            
            # Attach diagram to appropriate tweet
            if i == diagram_tweet_idx and diagram_path and diagram_path.exists():
                # Check file size
                file_size = diagram_path.stat().st_size
                if file_size > 5 * 1024 * 1024:
                    logger.warning(f"Diagram too large ({file_size} bytes): {diagram_path}")
                else:
                    tweet_dict['image_path'] = str(diagram_path)
                    logger.info(f"Attached diagram to tweet {i+1}: {diagram_path.name}")
                    
                    # Clean up diagram placeholder text if present
                    tweet_dict['text'] = re.sub(
                        r'\[.*?(Diagram|Flowchart|Chart).*?(Placeholder|Attached|Below).*?\]',
                        '', tweet_text, flags=re.IGNORECASE
                    ).strip()
            
            prepared_tweets.append(tweet_dict)
        
        if dry_run:
            self._print_dry_run_summary(topic, prepared_tweets)
        
        return prepared_tweets
    
    def _print_dry_run_summary(self, topic: str, tweets: List[Dict]):
        """Print a summary of what would be posted"""
        print("\n" + "="*60)
        print(f"🔍 DRY RUN - Thread: {topic}")
        print("="*60)
        
        for i, tweet in enumerate(tweets):
            print(f"\n📝 Tweet {i+1}/{len(tweets)}:")
            print(f"   Text: {tweet['text'][:100]}..." if len(tweet['text']) > 100 else f"   Text: {tweet['text']}")
            
            if 'image_path' in tweet:
                print(f"   📸 Image: {Path(tweet['image_path']).name}")
                print(f"   📁 Path: {tweet['image_path']}")
                if Path(tweet['image_path']).exists():
                    size = Path(tweet['image_path']).stat().st_size / 1024
                    print(f"   📊 Size: {size:.1f} KB")
                else:
                    print("   ⚠️  WARNING: Image file not found!")
        
        print("\n" + "="*60)
    
    def post_thread(self, thread_data: Dict, dry_run: bool = False) -> Optional[List[Dict]]:
        """
        Post a complete thread with media
        
        Args:
            thread_data: Thread JSON data
            dry_run: If True, only preview without posting
            
        Returns:
            List of response dictionaries or None if dry run
        """
        # Prepare tweets with media
        prepared_tweets = self.prepare_thread_with_media(thread_data, dry_run)
        
        if dry_run:
            return None
        
        # Initialize publisher if needed
        if not self.publisher:
            try:
                self.publisher = TwitterPublisher()
                logger.info("Twitter publisher initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Twitter publisher: {e}")
                raise
        
        # Post the thread
        topic = thread_data.get('topic', 'Unknown')
        logger.info(f"Posting thread: {topic} ({len(prepared_tweets)} tweets)")
        
        try:
            responses = self.publisher.post_thread_with_media(prepared_tweets)
            
            # Log success
            logger.info(f"✅ Successfully posted {len(responses)} tweets")
            for i, response in enumerate(responses):
                logger.info(f"   Tweet {i+1}: {response['url']}")
            
            # Save posting record
            self._save_posting_record(thread_data, prepared_tweets, responses)
            
            return responses
            
        except Exception as e:
            logger.error(f"❌ Failed to post thread: {e}")
            raise
    
    def _save_posting_record(self, thread_data: Dict, tweets: List[Dict], responses: List[Dict]):
        """Save a record of what was posted"""
        record = {
            'posted_at': datetime.now().isoformat(),
            'topic': thread_data.get('topic', 'Unknown'),
            'tweet_count': len(tweets),
            'tweets_with_media': sum(1 for t in tweets if 'image_path' in t),
            'responses': responses,
            'prepared_tweets': tweets
        }
        
        # Save to posted directory
        posted_dir = Path("posted_threads")
        posted_dir.mkdir(exist_ok=True)
        
        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{thread_data.get('topic', 'thread')[:30]}.json"
        filename = re.sub(r'[^\w\s-]', '', filename).strip()
        
        with open(posted_dir / filename, 'w') as f:
            json.dump(record, f, indent=2)
        
        logger.info(f"Posting record saved: {posted_dir / filename}")


def process_file(file_path: str, binder: TweetDiagramBinder, dry_run: bool = False) -> bool:
    """Process a single thread file"""
    logger.info(f"Processing: {file_path}")
    
    try:
        with open(file_path, 'r') as f:
            thread_data = json.load(f)
        
        binder.post_thread(thread_data, dry_run=dry_run)
        return True
        
    except Exception as e:
        logger.error(f"Failed to process {file_path}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Tweet + Diagram Binding and Publishing (Phase 4)"
    )
    parser.add_argument(
        "input",
        help="Input JSON file or directory containing thread files"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what would be posted without actually posting"
    )
    parser.add_argument(
        "--diagram-dir",
        default="/home/kushagra/X/optimized",
        help="Directory containing optimized diagram PNGs"
    )
    parser.add_argument(
        "--pattern",
        default="*.json",
        help="File pattern for batch processing (default: *.json)"
    )
    
    args = parser.parse_args()
    
    # Check credentials (unless dry run)
    if not args.dry_run:
        required_vars = ['API_KEY', 'API_SECRET', 'ACCESS_TOKEN', 'ACCESS_TOKEN_SECRET']
        missing = [var for var in required_vars if not os.environ.get(var)]
        
        if missing:
            print("❌ Missing Twitter API credentials:")
            for var in missing:
                print(f"   - {var}")
            print("\nSet them with:")
            print("   export API_KEY='your_api_key'")
            print("   export API_SECRET='your_api_secret'")
            print("   export ACCESS_TOKEN='your_access_token'")
            print("   export ACCESS_TOKEN_SECRET='your_access_token_secret'")
            sys.exit(1)
    
    # Initialize binder
    binder = TweetDiagramBinder(diagram_dir=args.diagram_dir)
    
    # Process input
    input_path = Path(args.input)
    
    if input_path.is_file():
        # Single file
        success = process_file(str(input_path), binder, dry_run=args.dry_run)
        sys.exit(0 if success else 1)
        
    elif input_path.is_dir():
        # Directory - batch process
        files = list(input_path.glob(args.pattern))
        logger.info(f"Found {len(files)} files to process")
        
        success_count = 0
        for file_path in files:
            if process_file(str(file_path), binder, dry_run=args.dry_run):
                success_count += 1
        
        logger.info(f"\n✅ Processed {success_count}/{len(files)} files successfully")
        
    else:
        logger.error(f"Input not found: {args.input}")
        sys.exit(1)


if __name__ == "__main__":
    main()