#!/usr/bin/env python3
"""
Analyze feedback to improve tweet generation
"""

import json
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime

class FeedbackAnalyzer:
    def __init__(self, feedback_file="feedback_log.json"):
        """Initialize with feedback data"""
        self.feedback_file = feedback_file
        self.load_feedback()
    
    def load_feedback(self):
        """Load feedback history"""
        if Path(self.feedback_file).exists():
            with open(self.feedback_file, 'r') as f:
                self.feedback_data = json.load(f)
        else:
            self.feedback_data = []
    
    def analyze_patterns(self):
        """Analyze feedback patterns to improve generation"""
        if not self.feedback_data:
            return {"message": "No feedback data available"}
        
        analysis = {
            "total_feedback": len(self.feedback_data),
            "feedback_types": Counter(),
            "rejection_reasons": [],
            "approved_patterns": [],
            "topic_performance": defaultdict(lambda: {"approved": 0, "rejected": 0})
        }
        
        for entry in self.feedback_data:
            feedback = entry['feedback']
            content = entry['content']
            
            # Count feedback types
            analysis['feedback_types'][feedback['type']] += 1
            
            # Analyze rejections
            if feedback['type'] == 'rejected' and 'reason' in feedback:
                analysis['rejection_reasons'].append({
                    "reason": feedback['reason'],
                    "topic": content.get('topic', 'Unknown')
                })
            
            # Analyze approvals
            elif feedback['type'] == 'approved':
                analysis['approved_patterns'].append({
                    "topic": content.get('topic', 'Unknown'),
                    "category": content.get('category', 'Unknown'),
                    "character_count": content['content']['character_count']
                })
            
            # Track topic performance
            topic = content.get('topic', 'Unknown')
            if feedback['type'] == 'approved':
                analysis['topic_performance'][topic]['approved'] += 1
            elif feedback['type'] == 'rejected':
                analysis['topic_performance'][topic]['rejected'] += 1
        
        return analysis
    
    def generate_insights(self):
        """Generate actionable insights from feedback"""
        analysis = self.analyze_patterns()
        
        if analysis.get("message"):
            return analysis
        
        insights = []
        
        # Approval rate
        total = analysis['total_feedback']
        approved = analysis['feedback_types'].get('approved', 0)
        approval_rate = (approved / total * 100) if total > 0 else 0
        
        insights.append(f"Approval rate: {approval_rate:.1f}%")
        
        # Most common rejection reasons
        if analysis['rejection_reasons']:
            reason_counts = Counter(r['reason'] for r in analysis['rejection_reasons'])
            top_reason = reason_counts.most_common(1)[0]
            insights.append(f"Top rejection reason: '{top_reason[0]}' ({top_reason[1]} times)")
        
        # Best performing topics
        topic_scores = []
        for topic, stats in analysis['topic_performance'].items():
            if stats['approved'] + stats['rejected'] > 0:
                success_rate = stats['approved'] / (stats['approved'] + stats['rejected'])
                topic_scores.append((topic, success_rate, stats['approved']))
        
        if topic_scores:
            topic_scores.sort(key=lambda x: x[1], reverse=True)
            best_topic = topic_scores[0]
            insights.append(f"Best performing topic: '{best_topic[0]}' ({best_topic[1]*100:.0f}% approval)")
        
        # Character count preferences
        if analysis['approved_patterns']:
            avg_chars = sum(p['character_count'] for p in analysis['approved_patterns']) / len(analysis['approved_patterns'])
            insights.append(f"Average approved tweet length: {avg_chars:.0f} characters")
        
        return {
            "insights": insights,
            "detailed_analysis": analysis
        }
    
    def export_learning_data(self, output_file="learning_data.json"):
        """Export data for model improvement"""
        learning_data = {
            "positive_examples": [],
            "negative_examples": [],
            "revision_pairs": []
        }
        
        for i, entry in enumerate(self.feedback_data):
            feedback = entry['feedback']
            content = entry['content']
            
            if feedback['type'] == 'approved':
                learning_data['positive_examples'].append({
                    "content": content['content']['full_text'],
                    "topic": content.get('topic'),
                    "category": content.get('category')
                })
            
            elif feedback['type'] == 'rejected':
                learning_data['negative_examples'].append({
                    "content": content['content']['full_text'],
                    "topic": content.get('topic'),
                    "reason": feedback.get('reason', 'Not specified')
                })
            
            # Look for revision patterns
            if feedback['type'] == 'revise' and i + 1 < len(self.feedback_data):
                next_entry = self.feedback_data[i + 1]
                if next_entry['content'].get('topic') == content.get('topic'):
                    learning_data['revision_pairs'].append({
                        "original": content['content']['full_text'],
                        "revised": next_entry['content']['content']['full_text'],
                        "feedback": feedback.get('reason')
                    })
        
        with open(output_file, 'w') as f:
            json.dump(learning_data, f, indent=2)
        
        return learning_data
    
    def generate_report(self):
        """Generate a comprehensive feedback report"""
        insights = self.generate_insights()
        
        if isinstance(insights, dict) and insights.get("message"):
            return insights["message"]
        
        report = "# Tweet Generation Feedback Report\n\n"
        report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        report += "## Key Insights\n\n"
        for insight in insights['insights']:
            report += f"- {insight}\n"
        
        report += "\n## Detailed Analysis\n\n"
        
        analysis = insights['detailed_analysis']
        
        # Feedback distribution
        report += "### Feedback Distribution\n"
        for feedback_type, count in analysis['feedback_types'].most_common():
            report += f"- {feedback_type}: {count}\n"
        
        # Topic performance
        report += "\n### Topic Performance\n"
        for topic, stats in list(analysis['topic_performance'].items())[:10]:
            total = stats['approved'] + stats['rejected']
            if total > 0:
                success_rate = stats['approved'] / total * 100
                report += f"- {topic}: {success_rate:.0f}% approval ({stats['approved']}/{total})\n"
        
        # Recent rejections
        if analysis['rejection_reasons']:
            report += "\n### Recent Rejection Reasons\n"
            for reason_entry in analysis['rejection_reasons'][-5:]:
                report += f"- Topic: {reason_entry['topic']}\n"
                report += f"  Reason: {reason_entry['reason']}\n"
        
        return report

def main():
    """Run analysis and generate reports"""
    analyzer = FeedbackAnalyzer()
    
    # Generate insights
    print("📊 FEEDBACK ANALYSIS")
    print("===================\n")
    
    insights = analyzer.generate_insights()
    
    if isinstance(insights, dict) and insights.get("message"):
        print(insights["message"])
        return
    
    # Display insights
    print("Key Insights:")
    for insight in insights['insights']:
        print(f"  • {insight}")
    
    # Generate and save report
    report = analyzer.generate_report()
    with open("feedback_report.md", "w") as f:
        f.write(report)
    print("\n📄 Full report saved to: feedback_report.md")
    
    # Export learning data
    learning_data = analyzer.export_learning_data()
    print(f"\n🎓 Learning data exported to: learning_data.json")
    print(f"  - Positive examples: {len(learning_data['positive_examples'])}")
    print(f"  - Negative examples: {len(learning_data['negative_examples'])}")
    print(f"  - Revision pairs: {len(learning_data['revision_pairs'])}")

if __name__ == "__main__":
    main()