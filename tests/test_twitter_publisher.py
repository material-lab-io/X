#!/usr/bin/env python3
"""
Test script for twitter_publisher module

Run this to verify your Twitter API credentials and test posting functionality.
"""

import os
import sys
from pathlib import Path
from twitter_publisher import TwitterPublisher, post_tweet_with_media


def test_credentials():
    """Test if Twitter API credentials are properly configured"""
    print("🔍 Testing Twitter API credentials...")
    
    required_vars = ['API_KEY', 'API_SECRET', 'ACCESS_TOKEN', 'ACCESS_TOKEN_SECRET']
    missing = []
    
    for var in required_vars:
        value = os.environ.get(var)
        if value:
            # Show first 4 chars only for security
            masked = value[:4] + '*' * (len(value) - 4)
            print(f"  ✓ {var}: {masked}")
        else:
            print(f"  ❌ {var}: Not set")
            missing.append(var)
    
    if missing:
        print("\n❌ Missing credentials. Set them with:")
        for var in missing:
            print(f"  export {var}='your_value'")
        return False
    
    return True


def test_initialization():
    """Test initializing the TwitterPublisher"""
    print("\n🔧 Testing TwitterPublisher initialization...")
    
    try:
        publisher = TwitterPublisher()
        print("  ✓ TwitterPublisher initialized successfully")
        return publisher
    except Exception as e:
        print(f"  ❌ Failed to initialize: {e}")
        return None


def test_api_connection(publisher):
    """Test API connection by verifying credentials"""
    print("\n🌐 Testing API connection...")
    
    try:
        # Verify credentials by getting authenticated user
        user = publisher.api.verify_credentials()
        print(f"  ✓ Connected as: @{user.screen_name}")
        print(f"  ✓ Name: {user.name}")
        print(f"  ✓ Followers: {user.followers_count}")
        return True
    except Exception as e:
        print(f"  ❌ API connection failed: {e}")
        return False


def test_media_upload(publisher):
    """Test media upload with a sample image"""
    print("\n📸 Testing media upload...")
    
    # Look for a test image
    test_images = [
        "diagrams/png/docker-architecture.png",
        "diagrams/png/microservices-communication-patterns.png",
        "automated_diagrams/png/docker-container-lifecycle-management.png",
        "automated_diagrams/png/microservices-communication-patterns.png"
    ]
    
    test_image = None
    for image in test_images:
        if Path(image).exists():
            test_image = image
            break
    
    if not test_image:
        print("  ⚠️  No test image found. Skipping media upload test.")
        print("     Generate some diagrams first using the automation pipeline.")
        return None
    
    try:
        print(f"  📤 Uploading: {test_image}")
        media_id = publisher.upload_media(test_image)
        print(f"  ✓ Media uploaded successfully")
        print(f"  ✓ Media ID: {media_id}")
        return media_id
    except Exception as e:
        print(f"  ❌ Media upload failed: {e}")
        return None


def test_posting(publisher, media_id=None):
    """Test posting a tweet (with confirmation)"""
    print("\n📝 Testing tweet posting...")
    
    test_text = "🧪 Test tweet from twitter_publisher.py - Testing API integration"
    
    if media_id:
        print(f"  ℹ️  Will post with media")
    
    print(f"\n  Tweet text: \"{test_text}\"")
    
    # Ask for confirmation
    response = input("\n  ⚠️  Post this test tweet? (yes/no): ").lower().strip()
    
    if response != 'yes':
        print("  ⏭️  Skipping tweet post test")
        return False
    
    try:
        if media_id:
            result = publisher.post_tweet(test_text, media_ids=[media_id])
        else:
            result = publisher.post_tweet(test_text)
        
        print(f"  ✓ Tweet posted successfully!")
        print(f"  ✓ Tweet ID: {result['id']}")
        print(f"  ✓ URL: {result['url']}")
        return True
    except Exception as e:
        print(f"  ❌ Tweet posting failed: {e}")
        return False


def main():
    print("🐦 Twitter Publisher Test Suite")
    print("=" * 40)
    
    # Test credentials
    if not test_credentials():
        sys.exit(1)
    
    # Test initialization
    publisher = test_initialization()
    if not publisher:
        sys.exit(1)
    
    # Test API connection
    if not test_api_connection(publisher):
        sys.exit(1)
    
    # Test media upload
    media_id = test_media_upload(publisher)
    
    # Test posting (optional)
    print("\n" + "=" * 40)
    print("All basic tests passed! ✓")
    print("\nYou can now:")
    print("1. Use post_tweet_with_media() function directly")
    print("2. Use post_generated_content.py to post threads")
    print("3. Integrate twitter_publisher into your pipeline")
    
    # Optional full test
    response = input("\nRun full posting test? (yes/no): ").lower().strip()
    if response == 'yes':
        test_posting(publisher, media_id)


if __name__ == "__main__":
    main()