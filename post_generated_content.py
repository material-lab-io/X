#!/usr/bin/env python3
"""
Integration script to post generated content to Twitter/X

This script demonstrates how to use the twitter_publisher module
with the existing content generation pipeline.
"""

import json
import os
import sys
from pathlib import Path
from typing import List, Dict
import argparse
import logging

from twitter_publisher import TwitterPublisher

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_thread_data(json_path: str) -> Dict:
    """Load generated thread data from JSON file"""
    with open(json_path, 'r') as f:
        return json.load(f)


def find_diagram_for_tweet(tweet_index: int, diagram_metadata: Dict) -> str:
    """
    Find the appropriate diagram for a tweet based on placement recommendations
    
    Args:
        tweet_index: Zero-based index of tweet in thread
        diagram_metadata: Metadata from diagram automation pipeline
        
    Returns:
        Path to PNG file or None
    """
    # Check if any diagrams have placement recommendations
    for diagram in diagram_metadata.get('diagrams', []):
        placement = diagram.get('placement_recommendation', {})
        recommended_position = placement.get('position')
        
        # Match tweet index with recommended position (1-based to 0-based)
        if recommended_position and recommended_position - 1 == tweet_index:
            png_path = diagram.get('png_path')
            if png_path and Path(png_path).exists():
                return png_path
    
    return None


def prepare_thread_for_posting(thread_data: Dict, diagram_dir: str = "diagrams") -> List[Dict]:
    """
    Prepare thread data for posting by matching tweets with diagrams
    
    Args:
        thread_data: Generated thread JSON data
        diagram_dir: Directory containing diagram metadata
        
    Returns:
        List of tweet dictionaries with text and optional image_path
    """
    tweets = []
    
    # Load diagram metadata if available
    metadata_path = Path(diagram_dir) / "metadata" / f"{thread_data['topic'].lower().replace(' ', '-')}_metadata.json"
    diagram_metadata = {}
    if metadata_path.exists():
        with open(metadata_path, 'r') as f:
            diagram_metadata = json.load(f)
    
    # Process each tweet
    for i, tweet in enumerate(thread_data['tweets']):
        tweet_dict = {'text': tweet}
        
        # Check for diagram placeholder
        if "[Diagram Placeholder]" in tweet:
            # Find corresponding diagram
            diagram_path = find_diagram_for_tweet(i, diagram_metadata)
            if diagram_path:
                tweet_dict['image_path'] = diagram_path
                # Remove placeholder from text
                tweet_dict['text'] = tweet.replace("[Diagram Placeholder]", "").strip()
        
        tweets.append(tweet_dict)
    
    return tweets


def post_thread(json_path: str, dry_run: bool = False) -> None:
    """
    Post a generated thread to Twitter/X
    
    Args:
        json_path: Path to generated thread JSON
        dry_run: If True, only show what would be posted
    """
    # Load thread data
    thread_data = load_thread_data(json_path)
    logger.info(f"Loaded thread: {thread_data['topic']} ({len(thread_data['tweets'])} tweets)")
    
    # Prepare tweets with media
    tweets = prepare_thread_for_posting(thread_data)
    
    if dry_run:
        print("\n=== DRY RUN - Would post the following thread ===\n")
        for i, tweet in enumerate(tweets):
            print(f"Tweet {i+1}:")
            print(f"Text: {tweet['text']}")
            if 'image_path' in tweet:
                print(f"Image: {tweet['image_path']}")
            print()
        return
    
    # Initialize publisher and post
    try:
        publisher = TwitterPublisher()
        
        # Post as thread
        print(f"\nPosting thread: {thread_data['topic']}...")
        responses = publisher.post_thread_with_media(tweets)
        
        print(f"\n✓ Successfully posted {len(responses)} tweets!")
        print(f"\nThread URL: {responses[0]['url']}")
        
        # Save posting record
        output_path = Path(json_path).with_suffix('.posted.json')
        with open(output_path, 'w') as f:
            json.dump({
                'original_file': json_path,
                'topic': thread_data['topic'],
                'posted_at': responses[0]['id'],
                'tweets': responses
            }, f, indent=2)
        
        print(f"\nPosting record saved to: {output_path}")
        
    except Exception as e:
        logger.error(f"Failed to post thread: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Post generated Twitter/X threads with media"
    )
    parser.add_argument(
        "json_file",
        help="Path to generated thread JSON file"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be posted without actually posting"
    )
    parser.add_argument(
        "--single-tweet",
        type=int,
        help="Post only a specific tweet number from the thread"
    )
    
    args = parser.parse_args()
    
    # Check for credentials
    required_vars = ['API_KEY', 'API_SECRET', 'ACCESS_TOKEN', 'ACCESS_TOKEN_SECRET']
    missing = [var for var in required_vars if not os.environ.get(var)]
    
    if missing and not args.dry_run:
        print("❌ Missing Twitter API credentials:")
        for var in missing:
            print(f"  - {var}")
        print("\nSet them with:")
        print("  export API_KEY='your_api_key'")
        print("  export API_SECRET='your_api_secret'")
        print("  export ACCESS_TOKEN='your_access_token'")
        print("  export ACCESS_TOKEN_SECRET='your_access_token_secret'")
        sys.exit(1)
    
    # Post thread
    post_thread(args.json_file, dry_run=args.dry_run)


if __name__ == "__main__":
    main()