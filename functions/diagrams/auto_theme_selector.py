#!/usr/bin/env python3
"""
Automatic PlantUML Theme Selector
Intelligently selects the best theme from 31 options based on topic/content
"""

from typing import Optional
import re

class AutoThemeSelector:
    """Automatically select PlantUML theme based on content"""
    
    def __init__(self):
        # Theme categories and mappings
        self.theme_mappings = {
            # Technical/Professional themes
            "aws-orange": ["aws", "cloud", "amazon", "s3", "ec2", "lambda"],
            "cloudscape-design": ["cloud", "infrastructure", "iaas", "paas", "saas"],
            "blueprint": ["architecture", "blueprint", "technical", "engineering", "design"],
            
            # Dark/Modern themes for real-time/data systems
            "cyborg": ["real-time", "streaming", "analytics", "dashboard", "monitoring"],
            "hacker": ["security", "hack", "penetration", "vulnerability", "cyber"],
            "black-knight": ["gaming", "game", "medieval", "fantasy"],
            "carbon-gray": ["data", "database", "storage", "warehouse"],
            
            # Light/Clean themes
            "lightgray": ["documentation", "docs", "guide", "tutorial"],
            "silver": ["enterprise", "corporate", "business", "professional"],
            "spacelab": ["science", "research", "lab", "experiment", "space"],
            
            # Colorful/Vibrant themes
            "vibrant": ["startup", "innovation", "creative", "new"],
            "cerulean": ["web", "frontend", "ui", "ux", "react", "angular", "vue"],
            "minty": ["fresh", "clean", "minimal", "simple"],
            "sunlust": ["warm", "friendly", "social", "community"],
            "sandstone": ["stable", "solid", "foundation", "core", "base"],
            
            # Specialized themes
            "mars": ["space", "nasa", "rocket", "astronomy", "exploration"],
            "superhero": ["hero", "super", "comic", "marvel", "power"],
            "toy": ["fun", "play", "game", "child", "education"],
            "amiga": ["retro", "vintage", "old", "classic", "legacy"],
            "crt-amber": ["terminal", "console", "cli", "command", "shell"],
            
            # Material/Modern themes
            "materia": ["material", "google", "android", "mobile", "app"],
            "metal": ["industrial", "hardware", "embedded", "iot", "device"],
            "sketchy": ["draft", "prototype", "mockup", "wireframe", "sketch"],
            
            # Professional variations
            "united": ["team", "collaboration", "together", "unified"],
            "bluegray": ["kubernetes", "k8s", "docker", "container", "microservice"],
            "reddress-darkblue": ["finance", "fintech", "banking", "trading"],
            "reddress-lightblue": ["healthcare", "medical", "health", "hospital"],
            
            # Special themes
            "mimeograph": ["document", "report", "paper", "print"],
            "mono": ["simple", "basic", "minimalist", "clean"],
            "plain": ["default", "standard", "normal"],
            "none": ["raw", "unstyled", "basic"]
        }
        
        # Default themes for common architectural patterns
        self.pattern_themes = {
            "microservices": "bluegray",
            "monolithic": "sandstone",
            "serverless": "aws-orange",
            "event-driven": "cyborg",
            "api": "cerulean",
            "database": "carbon-gray",
            "ml": "spacelab",
            "ai": "spacelab",
            "blockchain": "hacker",
            "iot": "metal"
        }

    def select_theme(self, topic: str, content: str = None, style: str = None) -> str:
        """
        Select the best theme based on topic and content
        
        Args:
            topic: The main topic/title
            content: Optional content/context
            style: Optional style preference (e.g., 'dark', 'light', 'colorful')
            
        Returns:
            Selected theme name
        """
        # Combine topic and content for analysis
        text = (topic + " " + (content or "")).lower()
        
        # Check for style preferences
        if style:
            style_lower = style.lower()
            if "dark" in style_lower:
                return self._select_dark_theme(text)
            elif "light" in style_lower:
                return self._select_light_theme(text)
            elif "colorful" in style_lower or "vibrant" in style_lower:
                return self._select_colorful_theme(text)
        
        # Score each theme based on keyword matches
        theme_scores = {}
        
        # Check keyword mappings
        for theme, keywords in self.theme_mappings.items():
            score = 0
            for keyword in keywords:
                if keyword in text:
                    # Higher score for exact word match
                    if re.search(r'\b' + keyword + r'\b', text):
                        score += 2
                    else:
                        score += 1
            
            if score > 0:
                theme_scores[theme] = score
        
        # Check architectural patterns
        for pattern, theme in self.pattern_themes.items():
            if pattern in text:
                theme_scores[theme] = theme_scores.get(theme, 0) + 3
        
        # Special case for real-time analytics (like the user's example)
        if ("real-time" in text or "realtime" in text) and ("analytics" in text or "dashboard" in text):
            theme_scores["cyborg"] = theme_scores.get("cyborg", 0) + 5
        
        # IoT and streaming
        if "iot" in text or "kafka" in text or "flink" in text or "streaming" in text:
            theme_scores["metal"] = theme_scores.get("metal", 0) + 3
            theme_scores["cyborg"] = theme_scores.get("cyborg", 0) + 2
        
        # Select theme with highest score
        if theme_scores:
            best_theme = max(theme_scores.items(), key=lambda x: x[1])[0]
            return best_theme
        
        # Default based on common patterns
        if any(word in text for word in ["api", "rest", "graphql", "endpoint"]):
            return "cerulean"
        elif any(word in text for word in ["data", "database", "sql", "storage"]):
            return "carbon-gray"
        elif any(word in text for word in ["cloud", "aws", "azure", "gcp"]):
            return "cloudscape-design"
        elif any(word in text for word in ["docker", "kubernetes", "container"]):
            return "bluegray"
        
        # Default theme
        return "blueprint"  # Good general technical theme
    
    def _select_dark_theme(self, text: str) -> str:
        """Select from dark themes"""
        dark_themes = ["cyborg", "hacker", "black-knight", "carbon-gray", "reddress-darkblue"]
        
        # Check for specific matches
        if "security" in text or "cyber" in text:
            return "hacker"
        elif "real-time" in text or "analytics" in text:
            return "cyborg"
        elif "data" in text or "database" in text:
            return "carbon-gray"
        elif "finance" in text or "trading" in text:
            return "reddress-darkblue"
        
        return "cyborg"  # Default dark theme
    
    def _select_light_theme(self, text: str) -> str:
        """Select from light themes"""
        light_themes = ["lightgray", "silver", "spacelab", "plain", "sandstone"]
        
        # Check for specific matches
        if "documentation" in text or "docs" in text:
            return "lightgray"
        elif "enterprise" in text or "corporate" in text:
            return "silver"
        elif "science" in text or "research" in text:
            return "spacelab"
        
        return "silver"  # Default light theme
    
    def _select_colorful_theme(self, text: str) -> str:
        """Select from colorful themes"""
        colorful_themes = ["vibrant", "cerulean", "minty", "Sunlust", "toy"]
        
        # Check for specific matches
        if "web" in text or "frontend" in text:
            return "cerulean"
        elif "startup" in text or "innovation" in text:
            return "vibrant"
        elif "minimal" in text or "simple" in text:
            return "minty"
        
        return "vibrant"  # Default colorful theme

    def get_theme_description(self, theme: str) -> str:
        """Get a description of why this theme was selected"""
        descriptions = {
            "cyborg": "Dark futuristic theme perfect for real-time systems and analytics",
            "metal": "Industrial theme ideal for IoT and hardware systems",
            "bluegray": "Professional theme for microservices and containerized apps",
            "carbon-gray": "Modern dark theme for data-intensive applications",
            "cloudscape-design": "AWS-inspired theme for cloud architectures",
            "blueprint": "Technical blueprint style for architectural diagrams",
            "cerulean": "Bright blue theme for web and API designs",
            "aws-orange": "Official AWS theme for cloud services",
            "hacker": "Matrix-style theme for security systems",
            "spacelab": "Clean scientific theme for research and ML/AI"
        }
        
        return descriptions.get(theme, f"Theme {theme} selected for optimal visualization")

# Convenience function
def auto_select_theme(topic: str, content: str = None, style: str = None) -> tuple[str, str]:
    """
    Automatically select the best PlantUML theme
    
    Returns:
        tuple of (theme_name, description)
    """
    selector = AutoThemeSelector()
    theme = selector.select_theme(topic, content, style)
    description = selector.get_theme_description(theme)
    return theme, description

if __name__ == "__main__":
    # Test the selector
    test_cases = [
        ("Building a Real-Time Analytics Platform", "Processing 10M events/sec from IoT devices using Kafka and Flink"),
        ("Microservices Architecture", "Docker and Kubernetes deployment"),
        ("AWS Cloud Infrastructure", "S3, Lambda, and DynamoDB"),
        ("Security Audit System", "Penetration testing and vulnerability scanning"),
        ("React Dashboard", "Frontend UI with WebSocket connections"),
        ("Database Design", "PostgreSQL with Redis caching"),
        ("Machine Learning Pipeline", "TensorFlow and PyTorch models")
    ]
    
    selector = AutoThemeSelector()
    
    print("Theme Selection Tests:")
    print("=" * 80)
    
    for topic, content in test_cases:
        theme = selector.select_theme(topic, content)
        desc = selector.get_theme_description(theme)
        print(f"\nTopic: {topic}")
        print(f"Content: {content}")
        print(f"Selected Theme: {theme}")
        print(f"Reason: {desc}")