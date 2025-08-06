#!/usr/bin/env python3
"""
Posting Summary Generator

Creates detailed logs and summaries of posted threads.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import argparse


class PostingSummary:
    """Generate summaries of posted threads"""
    
    def __init__(self, posted_dir: str = "posted_threads"):
        self.posted_dir = Path(posted_dir)
        self.posted_dir.mkdir(exist_ok=True)
    
    def generate_summary(self, posting_record: Dict) -> str:
        """Generate a human-readable summary from a posting record"""
        summary = []
        
        # Header
        summary.append("="*60)
        summary.append(f"📊 POSTING SUMMARY")
        summary.append("="*60)
        
        # Basic info
        summary.append(f"\n📌 Topic: {posting_record.get('topic', 'Unknown')}")
        summary.append(f"🕐 Posted at: {posting_record.get('posted_at', 'Unknown')}")
        summary.append(f"🧵 Total tweets: {posting_record.get('tweet_count', 0)}")
        summary.append(f"📸 Tweets with media: {posting_record.get('tweets_with_media', 0)}")
        
        # Tweet details
        summary.append("\n📝 TWEET DETAILS:")
        summary.append("-"*40)
        
        prepared_tweets = posting_record.get('prepared_tweets', [])
        responses = posting_record.get('responses', [])
        
        for i, (tweet, response) in enumerate(zip(prepared_tweets, responses)):
            summary.append(f"\nTweet {i+1}/{len(prepared_tweets)}:")
            
            # Tweet text (truncated)
            text = tweet.get('text', '')
            if len(text) > 100:
                summary.append(f"  Text: {text[:100]}...")
            else:
                summary.append(f"  Text: {text}")
            
            # Media info
            if 'image_path' in tweet:
                image_name = Path(tweet['image_path']).name
                summary.append(f"  📸 Image: {image_name}")
                summary.append(f"  ✅ Media uploaded successfully")
            
            # Response info
            if response:
                summary.append(f"  🔗 URL: {response.get('url', 'N/A')}")
                summary.append(f"  🆔 Tweet ID: {response.get('id', 'N/A')}")
        
        # Footer
        summary.append("\n" + "="*60)
        summary.append("✅ Thread posted successfully!")
        summary.append("="*60)
        
        return "\n".join(summary)
    
    def save_summary_report(self, posting_records: List[Dict]) -> Path:
        """Save a comprehensive summary report"""
        report_path = self.posted_dir / f"summary_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(report_path, 'w') as f:
            f.write("🐦 TWITTER POSTING SUMMARY REPORT\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*80 + "\n\n")
            
            # Overall statistics
            total_threads = len(posting_records)
            total_tweets = sum(r.get('tweet_count', 0) for r in posting_records)
            total_media = sum(r.get('tweets_with_media', 0) for r in posting_records)
            
            f.write("📊 OVERALL STATISTICS:\n")
            f.write(f"  • Total threads posted: {total_threads}\n")
            f.write(f"  • Total tweets: {total_tweets}\n")
            f.write(f"  • Tweets with media: {total_media}\n")
            f.write(f"  • Media attachment rate: {total_media/total_tweets*100:.1f}%\n\n")
            
            # Individual thread summaries
            f.write("📝 THREAD SUMMARIES:\n")
            f.write("="*80 + "\n")
            
            for i, record in enumerate(posting_records):
                f.write(f"\nThread {i+1}/{total_threads}:\n")
                f.write(self.generate_summary(record))
                f.write("\n\n")
        
        return report_path
    
    def analyze_posting_directory(self) -> Dict:
        """Analyze all posting records in the directory"""
        if not self.posted_dir.exists():
            return {"error": "No posted threads directory found"}
        
        posting_files = list(self.posted_dir.glob("*.json"))
        
        if not posting_files:
            return {"error": "No posting records found"}
        
        records = []
        for file in posting_files:
            try:
                with open(file, 'r') as f:
                    records.append(json.load(f))
            except Exception as e:
                print(f"Error reading {file}: {e}")
        
        # Generate analysis
        analysis = {
            "total_threads": len(records),
            "total_tweets": sum(r.get('tweet_count', 0) for r in records),
            "total_media": sum(r.get('tweets_with_media', 0) for r in records),
            "topics": [r.get('topic', 'Unknown') for r in records],
            "posting_times": [r.get('posted_at', 'Unknown') for r in records]
        }
        
        return analysis


def main():
    parser = argparse.ArgumentParser(description="Generate posting summaries")
    parser.add_argument(
        "--analyze",
        action="store_true",
        help="Analyze all posting records"
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate comprehensive report"
    )
    parser.add_argument(
        "--posted-dir",
        default="posted_threads",
        help="Directory containing posting records"
    )
    
    args = parser.parse_args()
    
    summary = PostingSummary(posted_dir=args.posted_dir)
    
    if args.analyze:
        analysis = summary.analyze_posting_directory()
        
        if "error" in analysis:
            print(f"❌ {analysis['error']}")
        else:
            print("\n📊 POSTING ANALYSIS")
            print("="*40)
            print(f"Total threads posted: {analysis['total_threads']}")
            print(f"Total tweets: {analysis['total_tweets']}")
            print(f"Tweets with media: {analysis['total_media']}")
            print(f"\nTopics posted:")
            for topic in analysis['topics']:
                print(f"  • {topic}")
    
    elif args.report:
        # Load all records
        posted_dir = Path(args.posted_dir)
        if not posted_dir.exists():
            print("❌ No posted threads directory found")
            return
        
        records = []
        for file in posted_dir.glob("*.json"):
            try:
                with open(file, 'r') as f:
                    records.append(json.load(f))
            except Exception as e:
                print(f"Error reading {file}: {e}")
        
        if records:
            report_path = summary.save_summary_report(records)
            print(f"✅ Report saved: {report_path}")
        else:
            print("❌ No posting records found")
    
    else:
        print("Use --analyze or --report to generate summaries")


if __name__ == "__main__":
    main()