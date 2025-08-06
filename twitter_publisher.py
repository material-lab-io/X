"""
Twitter/X Publisher Module

This module handles posting tweets with media attachments to Twitter/X using Tweepy.
Uses Tweepy v2 (Client) for tweeting and v1.1 (API) for media upload.
"""

import os
import tweepy
from pathlib import Path
from typing import Optional, Dict, List
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TwitterPublisher:
    """Handles Twitter/X posting with media support"""
    
    def __init__(self):
        """Initialize Twitter API clients from environment variables"""
        # Get credentials from environment
        api_key = os.environ.get('API_KEY')
        api_secret = os.environ.get('API_SECRET')
        access_token = os.environ.get('ACCESS_TOKEN')
        access_token_secret = os.environ.get('ACCESS_TOKEN_SECRET')
        
        # Validate credentials
        if not all([api_key, api_secret, access_token, access_token_secret]):
            raise ValueError(
                "Missing Twitter API credentials. Please set: "
                "API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET"
            )
        
        # Initialize v2 client for tweeting
        self.client = tweepy.Client(
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_token_secret
        )
        
        # Initialize v1.1 API for media upload
        auth = tweepy.OAuth1UserHandler(
            api_key, api_secret, access_token, access_token_secret
        )
        self.api = tweepy.API(auth)
        
        logger.info("Twitter publisher initialized successfully")
    
    def upload_media(self, image_path: str) -> str:
        """
        Upload media file to Twitter
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Media ID string for use in tweets
        """
        # Validate file exists
        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        # Check file size (Twitter limit is 5MB for images)
        file_size = path.stat().st_size
        if file_size > 5 * 1024 * 1024:
            raise ValueError(f"Image file too large: {file_size} bytes (max 5MB)")
        
        # Upload media
        try:
            media = self.api.media_upload(filename=str(path))
            logger.info(f"Media uploaded successfully: {media.media_id}")
            return media.media_id_string
        except Exception as e:
            logger.error(f"Failed to upload media: {e}")
            raise
    
    def post_tweet(self, text: str, media_ids: Optional[List[str]] = None) -> Dict:
        """
        Post a tweet with optional media
        
        Args:
            text: Tweet text (max 280 characters)
            media_ids: List of media ID strings
            
        Returns:
            API response dictionary
        """
        # Validate tweet length
        if len(text) > 280:
            raise ValueError(f"Tweet too long: {len(text)} characters (max 280)")
        
        try:
            response = self.client.create_tweet(
                text=text,
                media_ids=media_ids
            )
            
            # Extract tweet data from response
            tweet_data = response.data
            logger.info(f"Tweet posted successfully: {tweet_data['id']}")
            
            return {
                'id': tweet_data['id'],
                'text': tweet_data['text'],
                'url': f"https://twitter.com/i/web/status/{tweet_data['id']}"
            }
        except Exception as e:
            logger.error(f"Failed to post tweet: {e}")
            raise
    
    def post_tweet_with_media(self, text: str, image_path: str) -> Dict:
        """
        Posts a tweet with the given text and image
        
        Args:
            text: Tweet text (max 280 characters)
            image_path: Path to the image file
            
        Returns:
            API response dictionary with tweet details
        """
        # Upload media first
        media_id = self.upload_media(image_path)
        
        # Post tweet with media
        return self.post_tweet(text, media_ids=[media_id])
    
    def post_thread_with_media(self, tweets: List[Dict[str, str]]) -> List[Dict]:
        """
        Post a thread of tweets with optional media
        
        Args:
            tweets: List of dicts with 'text' and optional 'image_path' keys
            
        Returns:
            List of API responses for each tweet
        """
        responses = []
        reply_to_id = None
        
        for i, tweet in enumerate(tweets):
            text = tweet['text']
            image_path = tweet.get('image_path')
            
            # Upload media if provided
            media_ids = None
            if image_path:
                media_id = self.upload_media(image_path)
                media_ids = [media_id]
            
            # Post tweet
            try:
                if reply_to_id:
                    # Reply to previous tweet in thread
                    response = self.client.create_tweet(
                        text=text,
                        in_reply_to_tweet_id=reply_to_id,
                        media_ids=media_ids
                    )
                else:
                    # First tweet in thread
                    response = self.client.create_tweet(
                        text=text,
                        media_ids=media_ids
                    )
                
                tweet_data = response.data
                reply_to_id = tweet_data['id']
                
                result = {
                    'id': tweet_data['id'],
                    'text': tweet_data['text'],
                    'url': f"https://twitter.com/i/web/status/{tweet_data['id']}",
                    'position': i + 1
                }
                responses.append(result)
                logger.info(f"Posted tweet {i+1}/{len(tweets)}: {tweet_data['id']}")
                
            except Exception as e:
                logger.error(f"Failed to post tweet {i+1}: {e}")
                raise
        
        return responses


# Standalone function for simple use cases
def post_tweet_with_media(text: str, image_path: str) -> dict:
    """
    Posts a tweet with the given text and image. Returns the API response.
    
    Args:
        text: Tweet text (max 280 characters)
        image_path: Path to the image file
        
    Returns:
        Dictionary containing tweet ID, text, and URL
    """
    publisher = TwitterPublisher()
    return publisher.post_tweet_with_media(text, image_path)


# Example usage and testing
if __name__ == "__main__":
    # Test credentials
    try:
        publisher = TwitterPublisher()
        print("✓ Twitter publisher initialized successfully")
        
        # Example: Post a single tweet with media
        # result = post_tweet_with_media(
        #     "Check out this architecture diagram!",
        #     "diagrams/png/docker-architecture.png"
        # )
        # print(f"Tweet posted: {result['url']}")
        
        # Example: Post a thread with media
        # thread = [
        #     {
        #         "text": "🧵 Let's talk about microservices architecture",
        #         "image_path": "diagrams/png/microservices-overview.png"
        #     },
        #     {
        #         "text": "First, understanding service communication patterns is crucial"
        #     },
        #     {
        #         "text": "Here's how async messaging works:",
        #         "image_path": "diagrams/png/async-messaging.png"
        #     }
        # ]
        # responses = publisher.post_thread_with_media(thread)
        # print(f"Thread posted: {len(responses)} tweets")
        
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("\nPlease set the following environment variables:")
        print("  export API_KEY='your_api_key'")
        print("  export API_SECRET='your_api_secret'")
        print("  export ACCESS_TOKEN='your_access_token'")
        print("  export ACCESS_TOKEN_SECRET='your_access_token_secret'")
    except Exception as e:
        print(f"❌ Error: {e}")