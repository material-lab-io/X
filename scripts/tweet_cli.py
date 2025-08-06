#!/usr/bin/env python3
"""
CLI tool for tweet generation with feedback loop
"""

import json
import os
from pathlib import Path
from datetime import datetime
import sys

class TweetCLI:
    def __init__(self):
        """Initialize CLI with generator"""
        from simple_tweet_generator import SimpleTweetGenerator
        self.generator = SimpleTweetGenerator()
        self.feedback_file = "feedback_log.json"
        self.load_feedback()
    
    def load_feedback(self):
        """Load previous feedback"""
        if Path(self.feedback_file).exists():
            with open(self.feedback_file, 'r') as f:
                self.feedback_history = json.load(f)
        else:
            self.feedback_history = []
    
    def save_feedback(self, content, feedback):
        """Save feedback for future learning"""
        feedback_entry = {
            "timestamp": datetime.now().isoformat(),
            "content": content,
            "feedback": feedback
        }
        self.feedback_history.append(feedback_entry)
        
        with open(self.feedback_file, 'w') as f:
            json.dump(self.feedback_history, f, indent=2)
    
    def display_tweet(self, tweet_content):
        """Display tweet with formatting"""
        print("\n" + "="*60)
        print("📱 GENERATED TWEET")
        print("="*60)
        print(tweet_content)
        print("="*60)
        print(f"Characters: {len(tweet_content)}/280")
        print("="*60 + "\n")
    
    def display_thread(self, tweets):
        """Display thread with formatting"""
        print("\n" + "="*60)
        print("🧵 GENERATED THREAD")
        print("="*60)
        for tweet in tweets:
            print(f"\n--- Tweet {tweet['position']} ---")
            print(tweet['content'])
            print(f"({tweet['character_count']} characters)")
        print("\n" + "="*60 + "\n")
    
    def get_feedback(self):
        """Get user feedback on generated content"""
        print("\n📊 FEEDBACK OPTIONS:")
        print("1. ✅ Approve - Save and use this tweet")
        print("2. 🛠️  Revise - Generate a new version")
        print("3. 💡 Alternative - Generate different approach")
        print("4. ✏️  Edit - Make manual changes")
        print("5. ❌ Reject - Discard this tweet")
        print("6. 📋 Copy - Copy to clipboard and exit")
        
        choice = input("\nYour choice (1-6): ").strip()
        
        feedback_map = {
            "1": "approved",
            "2": "revise",
            "3": "alternative",
            "4": "edit",
            "5": "rejected",
            "6": "copy"
        }
        
        if choice in feedback_map:
            feedback_type = feedback_map[choice]
            
            if feedback_type in ["revise", "alternative", "rejected"]:
                reason = input("Please provide specific feedback: ").strip()
                return {"type": feedback_type, "reason": reason}
            elif feedback_type == "edit":
                edited = input("Enter your edited version:\n").strip()
                return {"type": feedback_type, "edited_content": edited}
            else:
                return {"type": feedback_type}
        
        return {"type": "invalid"}
    
    def generate_single_interactive(self, topic, category=None):
        """Generate single tweet with feedback loop"""
        attempts = 0
        max_attempts = 5
        
        while attempts < max_attempts:
            attempts += 1
            print(f"\n🔄 Generation attempt {attempts}/{max_attempts}")
            
            # Generate tweet
            result = self.generator.generate_single_tweet(topic, category)
            tweet_content = result['content']['full_text']
            
            # Display
            self.display_tweet(tweet_content)
            
            # Get feedback
            feedback = self.get_feedback()
            
            # Process feedback
            if feedback['type'] == 'approved':
                print("✅ Tweet approved!")
                self.save_feedback(result, feedback)
                self.generator.save_output(result)
                return result
            
            elif feedback['type'] == 'copy':
                print("📋 Tweet copied to clipboard (simulated)")
                print(f"\nTweet text:\n{tweet_content}")
                return result
            
            elif feedback['type'] == 'edit':
                result['content']['full_text'] = feedback['edited_content']
                result['content']['character_count'] = len(feedback['edited_content'])
                print("✏️  Tweet edited and saved!")
                self.save_feedback(result, feedback)
                self.generator.save_output(result)
                return result
            
            elif feedback['type'] == 'revise':
                print(f"🛠️  Revising based on feedback: {feedback.get('reason', 'No specific reason')}")
                # In a real implementation, this would adjust generation parameters
                continue
            
            elif feedback['type'] == 'alternative':
                print("💡 Generating alternative approach...")
                # Change generation style
                continue
            
            elif feedback['type'] == 'rejected':
                print("❌ Tweet rejected. Generating new version...")
                self.save_feedback(result, feedback)
                continue
        
        print(f"\n⚠️  Reached maximum attempts ({max_attempts}). Please try a different topic.")
        return None
    
    def generate_thread_interactive(self, topic, category=None, length=5):
        """Generate thread with feedback loop"""
        attempts = 0
        max_attempts = 3
        
        while attempts < max_attempts:
            attempts += 1
            print(f"\n🔄 Generation attempt {attempts}/{max_attempts}")
            
            # Generate thread
            result = self.generator.generate_thread(topic, category, length)
            
            # Display
            self.display_thread(result['tweets'])
            
            # Get feedback
            feedback = self.get_feedback()
            
            # Process feedback
            if feedback['type'] == 'approved':
                print("✅ Thread approved!")
                self.save_feedback(result, feedback)
                self.generator.save_output(result)
                return result
            
            elif feedback['type'] == 'copy':
                print("📋 Thread copied to clipboard (simulated)")
                for tweet in result['tweets']:
                    print(f"\nTweet {tweet['position']}:\n{tweet['content']}")
                return result
            
            elif feedback['type'] in ['revise', 'alternative']:
                print(f"🛠️  Regenerating thread...")
                continue
            
            elif feedback['type'] == 'rejected':
                print("❌ Thread rejected. Generating new version...")
                self.save_feedback(result, feedback)
                continue
        
        print(f"\n⚠️  Reached maximum attempts ({max_attempts}). Please try a different topic.")
        return None
    
    def run(self):
        """Main CLI loop"""
        print("\n🐦 TWITTER/X CONTENT GENERATOR")
        print("================================")
        print("Generate engaging technical content for Twitter/X")
        print("Type 'help' for commands or 'exit' to quit\n")
        
        while True:
            command = input("\n> ").strip().lower()
            
            if command == 'exit':
                print("👋 Goodbye!")
                break
            
            elif command == 'help':
                print("\nCOMMANDS:")
                print("  single <topic>  - Generate a single tweet")
                print("  thread <topic>  - Generate a thread")
                print("  stats          - Show generation statistics")
                print("  help           - Show this help")
                print("  exit           - Exit the program")
            
            elif command.startswith('single '):
                topic = command[7:].strip()
                if topic:
                    self.generate_single_interactive(topic)
                else:
                    print("❌ Please provide a topic")
            
            elif command.startswith('thread '):
                topic = command[7:].strip()
                if topic:
                    # Ask for thread length
                    length_input = input("Thread length (3-7, default 5): ").strip()
                    try:
                        length = int(length_input) if length_input else 5
                        length = max(3, min(7, length))
                    except:
                        length = 5
                    
                    self.generate_thread_interactive(topic, length=length)
                else:
                    print("❌ Please provide a topic")
            
            elif command == 'stats':
                self.show_statistics()
            
            else:
                print("❌ Unknown command. Type 'help' for available commands.")
    
    def show_statistics(self):
        """Show generation and feedback statistics"""
        total = len(self.feedback_history)
        if total == 0:
            print("\n📊 No generation history yet.")
            return
        
        approved = sum(1 for f in self.feedback_history if f['feedback']['type'] == 'approved')
        rejected = sum(1 for f in self.feedback_history if f['feedback']['type'] == 'rejected')
        edited = sum(1 for f in self.feedback_history if f['feedback']['type'] == 'edit')
        
        print("\n📊 GENERATION STATISTICS")
        print("========================")
        print(f"Total generations: {total}")
        print(f"Approved: {approved} ({approved/total*100:.1f}%)")
        print(f"Rejected: {rejected} ({rejected/total*100:.1f}%)")
        print(f"Edited: {edited} ({edited/total*100:.1f}%)")
        
        # Show recent feedback
        if len(self.feedback_history) > 0:
            print("\nRECENT FEEDBACK:")
            for entry in self.feedback_history[-3:]:
                timestamp = entry['timestamp'][:19]
                feedback_type = entry['feedback']['type']
                print(f"- {timestamp}: {feedback_type}")

def main():
    """Run the CLI"""
    cli = TweetCLI()
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        command = ' '.join(sys.argv[1:])
        if command.startswith('single '):
            topic = command[7:]
            cli.generate_single_interactive(topic)
        elif command.startswith('thread '):
            topic = command[7:]
            cli.generate_thread_interactive(topic)
        else:
            cli.run()
    else:
        cli.run()

if __name__ == "__main__":
    main()