#!/usr/bin/env python3
"""
Enhanced Web interface for the Twitter/X content generator with full functionality
"""

from flask import Flask, render_template_string, request, jsonify, session
import json
from datetime import datetime
from pathlib import Path
import os
import secrets
import subprocess
from typing import Dict, List, Optional

# Import all generators
from unified_tweet_generator import UnifiedTweetGenerator
from tweet_generator import TweetGenerator
from simple_tweet_generator import SimpleTweetGenerator
from style_aware_generator import StyleAwareTweetGenerator

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Initialize generators
try:
    with open('config.json', 'r') as f:
        config = json.load(f)
        gemini_key = config.get('api_keys', {}).get('gemini')
        claude_key = config.get('api_keys', {}).get('anthropic')
        openai_key = config.get('api_keys', {}).get('openai')
except:
    gemini_key = os.environ.get('GEMINI_API_KEY', '')
    claude_key = os.environ.get('CLAUDE_API_KEY', '')
    openai_key = os.environ.get('OPENAI_API_KEY', '')

# Initialize all generators
generators = {
    'unified': UnifiedTweetGenerator(gemini_key, auto_polish=True) if gemini_key else None,
    'multi_model': TweetGenerator() if gemini_key else None,
    'simple': SimpleTweetGenerator(),
    'style_aware': StyleAwareTweetGenerator()
}

# Enhanced HTML template with all features
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Twitter/X AI Content Generator - Full Featured</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        :root {
            --twitter-blue: #1DA1F2;
            --twitter-dark: #14171A;
            --twitter-gray: #657786;
            --twitter-light-gray: #AAB8C2;
            --twitter-extra-light: #E1E8ED;
            --twitter-background: #F5F8FA;
            --success: #17BF63;
            --warning: #FFAD1F;
            --danger: #E0245E;
        }
        
        * {
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            margin: 0;
            padding: 0;
            background: var(--twitter-background);
            color: var(--twitter-dark);
        }
        
        .header {
            background: white;
            border-bottom: 1px solid var(--twitter-extra-light);
            padding: 20px 0;
            position: sticky;
            top: 0;
            z-index: 100;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        
        .header-content {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        
        .logo {
            display: flex;
            align-items: center;
            gap: 15px;
        }
        
        .logo h1 {
            margin: 0;
            color: var(--twitter-blue);
            font-size: 24px;
        }
        
        .stats-bar {
            display: flex;
            gap: 30px;
        }
        
        .stat-item {
            text-align: center;
        }
        
        .stat-value {
            font-size: 20px;
            font-weight: bold;
            color: var(--twitter-blue);
        }
        
        .stat-label {
            font-size: 12px;
            color: var(--twitter-gray);
        }
        
        .main-container {
            max-width: 1200px;
            margin: 30px auto;
            padding: 0 20px;
            display: grid;
            grid-template-columns: 350px 1fr;
            gap: 30px;
        }
        
        .sidebar {
            background: white;
            border-radius: 16px;
            padding: 25px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            height: fit-content;
            position: sticky;
            top: 100px;
        }
        
        .content-area {
            background: white;
            border-radius: 16px;
            padding: 25px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        
        .form-section {
            margin-bottom: 20px;
        }
        
        .form-section label {
            display: block;
            font-weight: 600;
            margin-bottom: 8px;
            color: var(--twitter-dark);
        }
        
        .form-control {
            width: 100%;
            padding: 12px;
            border: 2px solid var(--twitter-extra-light);
            border-radius: 8px;
            font-size: 14px;
            transition: all 0.2s;
        }
        
        .form-control:focus {
            outline: none;
            border-color: var(--twitter-blue);
        }
        
        textarea.form-control {
            resize: vertical;
            min-height: 80px;
        }
        
        .advanced-options {
            background: var(--twitter-background);
            border-radius: 8px;
            padding: 15px;
            margin-top: 20px;
        }
        
        .toggle-advanced {
            background: none;
            border: none;
            color: var(--twitter-blue);
            cursor: pointer;
            font-size: 14px;
            padding: 5px 0;
            display: flex;
            align-items: center;
            gap: 5px;
        }
        
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 24px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            font-size: 16px;
        }
        
        .btn-primary {
            background: var(--twitter-blue);
            color: white;
            width: 100%;
        }
        
        .btn-primary:hover {
            background: #1a8cd8;
        }
        
        .btn-primary:disabled {
            background: var(--twitter-light-gray);
            cursor: not-allowed;
        }
        
        .btn-secondary {
            background: white;
            color: var(--twitter-blue);
            border: 2px solid var(--twitter-blue);
        }
        
        .btn-secondary:hover {
            background: var(--twitter-background);
        }
        
        .btn-small {
            padding: 8px 16px;
            font-size: 14px;
        }
        
        .loading {
            display: none;
            text-align: center;
            padding: 40px;
        }
        
        .spinner {
            border: 3px solid var(--twitter-extra-light);
            border-top: 3px solid var(--twitter-blue);
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .output-section {
            display: none;
        }
        
        .tweet-card {
            background: white;
            border: 1px solid var(--twitter-extra-light);
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 20px;
            transition: all 0.2s;
        }
        
        .tweet-card:hover {
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        
        .tweet-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 15px;
            border-bottom: 1px solid var(--twitter-extra-light);
        }
        
        .tweet-number {
            font-weight: 600;
            color: var(--twitter-dark);
        }
        
        .char-count {
            font-size: 14px;
            color: var(--twitter-gray);
        }
        
        .char-count.warning {
            color: var(--warning);
        }
        
        .char-count.danger {
            color: var(--danger);
        }
        
        .tweet-content {
            font-size: 16px;
            line-height: 1.5;
            white-space: pre-wrap;
            margin-bottom: 15px;
        }
        
        .tweet-actions {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        
        .action-btn {
            padding: 8px 16px;
            border: 1px solid var(--twitter-extra-light);
            background: white;
            border-radius: 20px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            gap: 5px;
        }
        
        .action-btn:hover {
            background: var(--twitter-background);
            border-color: var(--twitter-blue);
            color: var(--twitter-blue);
        }
        
        .feedback-section {
            background: var(--twitter-background);
            border-radius: 12px;
            padding: 20px;
            margin-top: 20px;
        }
        
        .feedback-options {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 10px;
            margin-top: 15px;
        }
        
        .feedback-btn {
            padding: 12px;
            border: 2px solid transparent;
            background: white;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s;
            text-align: center;
        }
        
        .feedback-btn:hover {
            border-color: var(--twitter-blue);
        }
        
        .feedback-btn.selected {
            background: var(--twitter-blue);
            color: white;
        }
        
        .metadata-section {
            background: var(--twitter-background);
            border-radius: 8px;
            padding: 15px;
            margin-top: 15px;
            font-size: 14px;
        }
        
        .metadata-item {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
        }
        
        .metadata-label {
            color: var(--twitter-gray);
        }
        
        .metadata-value {
            font-weight: 600;
            color: var(--twitter-dark);
        }
        
        .category-tags {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            margin-top: 10px;
        }
        
        .category-tag {
            padding: 4px 12px;
            background: var(--twitter-blue);
            color: white;
            border-radius: 16px;
            font-size: 12px;
        }
        
        .history-section {
            margin-top: 30px;
        }
        
        .history-item {
            background: var(--twitter-background);
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 10px;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .history-item:hover {
            background: var(--twitter-extra-light);
        }
        
        .history-timestamp {
            font-size: 12px;
            color: var(--twitter-gray);
        }
        
        .history-preview {
            font-size: 14px;
            margin-top: 5px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        
        @media (max-width: 768px) {
            .main-container {
                grid-template-columns: 1fr;
            }
            
            .sidebar {
                position: static;
            }
            
            .feedback-options {
                grid-template-columns: 1fr;
            }
        }
        
        .toast {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: var(--twitter-dark);
            color: white;
            padding: 16px 24px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            display: none;
            z-index: 1000;
        }
        
        .toast.success {
            background: var(--success);
        }
        
        .toast.error {
            background: var(--danger);
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="header-content">
            <div class="logo">
                <h1>🐦 Twitter/X AI Content Generator</h1>
                <span style="color: var(--twitter-gray);">Full Featured Edition</span>
            </div>
            <div class="stats-bar">
                <div class="stat-item">
                    <div class="stat-value" id="totalGenerated">0</div>
                    <div class="stat-label">Generated</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value" id="avgScore">0</div>
                    <div class="stat-label">Avg Score</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value" id="savedCount">0</div>
                    <div class="stat-label">Saved</div>
                </div>
            </div>
        </div>
    </div>

    <div class="main-container">
        <div class="sidebar">
            <form id="generatorForm">
                <div class="form-section">
                    <label for="topic">Topic / Subject *</label>
                    <input type="text" id="topic" name="topic" class="form-control" 
                           placeholder="e.g., Docker optimization, AI agent debugging" required>
                </div>
                
                <div class="form-section">
                    <label for="contentType">Content Type</label>
                    <select id="contentType" name="contentType" class="form-control">
                        <option value="single">Single Tweet</option>
                        <option value="thread">Thread (5-7 tweets)</option>
                    </select>
                </div>
                
                <div class="form-section">
                    <label for="category">Category</label>
                    <select id="category" name="category" class="form-control">
                        <option value="auto">Auto-detect</option>
                        <option value="ai_agents">AI Agent Testing</option>
                        <option value="docker">Docker</option>
                        <option value="video_models">Video Models</option>
                        <option value="llms">LLMs</option>
                        <option value="devtools">DevTools</option>
                        <option value="coding">Agentic Coding</option>
                    </select>
                </div>
                
                <div class="form-section">
                    <label for="tone">Tone / Style</label>
                    <select id="tone" name="tone" class="form-control">
                        <option value="explanatory">Explanatory</option>
                        <option value="observational">Observational</option>
                        <option value="first_principles">First Principles</option>
                        <option value="build_in_public">Build in Public</option>
                        <option value="technical_deep_dive">Technical Deep Dive</option>
                        <option value="problem_solution">Problem/Solution</option>
                    </select>
                </div>
                
                <div class="form-section">
                    <label for="template">Template</label>
                    <select id="template" name="template" class="form-control">
                        <option value="auto">Auto-select</option>
                        <option value="problem_solution">Problem/Solution</option>
                        <option value="conceptual">Conceptual Deep Dive</option>
                        <option value="workflow">Workflow/Tools Share</option>
                        <option value="learning">Learning/Discovery</option>
                        <option value="announcement">Announcement</option>
                    </select>
                </div>
                
                <button type="button" class="toggle-advanced" onclick="toggleAdvanced()">
                    <span id="advancedToggle">▶</span> Advanced Options
                </button>
                
                <div id="advancedOptions" class="advanced-options" style="display: none;">
                    <div class="form-section">
                        <label for="context">Additional Context</label>
                        <textarea id="context" name="context" class="form-control" 
                                  placeholder="e.g., specific problem solved, technical details"></textarea>
                    </div>
                    
                    <div class="form-section">
                        <label for="generator">Generator Model</label>
                        <select id="generator" name="generator" class="form-control">
                            <option value="unified">Unified (Gemini + Templates)</option>
                            <option value="multi_model">Multi-Model (Gemini → Claude → OpenAI)</option>
                            <option value="style_aware">Style-Aware (Strict Guide)</option>
                            <option value="simple">Simple (Pattern-Based)</option>
                        </select>
                    </div>
                    
                    <div class="form-section">
                        <label for="includeDiagram">
                            <input type="checkbox" id="includeDiagram" name="includeDiagram">
                            Include Technical Diagram
                        </label>
                    </div>
                    
                    <div class="form-section">
                        <label for="includeLinks">
                            <input type="checkbox" id="includeLinks" name="includeLinks" checked>
                            Include Relevant Links
                        </label>
                    </div>
                    
                    <div class="form-section">
                        <label for="autoPolish">
                            <input type="checkbox" id="autoPolish" name="autoPolish" checked>
                            Auto-Polish Output
                        </label>
                    </div>
                </div>
                
                <button type="submit" id="generateBtn" class="btn btn-primary">
                    Generate Content
                </button>
            </form>
            
            <div class="history-section">
                <h3>Recent Generations</h3>
                <div id="historyList"></div>
            </div>
        </div>
        
        <div class="content-area">
            <div class="loading" id="loading">
                <div class="spinner"></div>
                <p>Generating your content...</p>
                <p style="font-size: 14px; color: var(--twitter-gray);">
                    Using <span id="currentModel">Gemini</span> model...
                </p>
            </div>
            
            <div id="output" class="output-section">
                <h2>Generated Content</h2>
                
                <div class="metadata-section">
                    <div class="metadata-item">
                        <span class="metadata-label">Model Used:</span>
                        <span class="metadata-value" id="modelUsed">-</span>
                    </div>
                    <div class="metadata-item">
                        <span class="metadata-label">Template:</span>
                        <span class="metadata-value" id="templateUsed">-</span>
                    </div>
                    <div class="metadata-item">
                        <span class="metadata-label">Generation Time:</span>
                        <span class="metadata-value" id="generationTime">-</span>
                    </div>
                </div>
                
                <div id="generatedContent"></div>
                
                <div class="feedback-section">
                    <h3>How was this content?</h3>
                    <div class="feedback-options">
                        <button class="feedback-btn" onclick="submitFeedback('great')">
                            😍 Great
                        </button>
                        <button class="feedback-btn" onclick="submitFeedback('good')">
                            👍 Good
                        </button>
                        <button class="feedback-btn" onclick="submitFeedback('okay')">
                            😐 Okay
                        </button>
                        <button class="feedback-btn" onclick="submitFeedback('needs_work')">
                            🛠️ Needs Work
                        </button>
                        <button class="feedback-btn" onclick="submitFeedback('poor')">
                            👎 Poor
                        </button>
                    </div>
                    <div style="margin-top: 15px;">
                        <textarea id="feedbackDetails" class="form-control" 
                                  placeholder="Additional feedback (optional)"></textarea>
                        <button class="btn btn-secondary btn-small" style="margin-top: 10px;"
                                onclick="saveFeedback()">Save Feedback</button>
                    </div>
                </div>
            </div>
            
            <div id="emptyState" style="text-align: center; padding: 60px; color: var(--twitter-gray);">
                <h2>Welcome to the Twitter/X Content Generator</h2>
                <p>Enter a topic and click "Generate Content" to create engaging tweets!</p>
                <p>This enhanced version includes all features from the CLI tool.</p>
            </div>
        </div>
    </div>
    
    <div id="toast" class="toast"></div>

    <script>
        let currentContent = null;
        let generationHistory = JSON.parse(localStorage.getItem('tweetHistory') || '[]');
        let stats = JSON.parse(localStorage.getItem('tweetStats') || '{"total": 0, "totalChars": 0, "feedbackScores": [], "saved": 0}');
        
        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            updateStats();
            loadHistory();
        });
        
        function toggleAdvanced() {
            const options = document.getElementById('advancedOptions');
            const toggle = document.getElementById('advancedToggle');
            
            if (options.style.display === 'none') {
                options.style.display = 'block';
                toggle.textContent = '▼';
            } else {
                options.style.display = 'none';
                toggle.textContent = '▶';
            }
        }
        
        document.getElementById('generatorForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData);
            
            // Convert checkboxes
            data.includeDiagram = formData.get('includeDiagram') === 'on';
            data.includeLinks = formData.get('includeLinks') === 'on';
            data.autoPolish = formData.get('autoPolish') === 'on';
            
            // Hide empty state
            document.getElementById('emptyState').style.display = 'none';
            
            // Show loading
            document.getElementById('loading').style.display = 'block';
            document.getElementById('currentModel').textContent = getModelName(data.generator);
            document.getElementById('generateBtn').disabled = true;
            document.getElementById('output').style.display = 'none';
            
            const startTime = Date.now();
            
            try {
                const response = await fetch('/generate_enhanced', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                if (result.error) {
                    showToast('Error: ' + result.error, 'error');
                } else {
                    result.generationTime = ((Date.now() - startTime) / 1000).toFixed(1) + 's';
                    displayContent(result);
                    updateStats();
                    addToHistory(data.topic, result);
                }
            } catch (error) {
                showToast('Error generating content: ' + error.message, 'error');
            } finally {
                document.getElementById('loading').style.display = 'none';
                document.getElementById('generateBtn').disabled = false;
            }
        });
        
        function getModelName(generator) {
            const names = {
                'unified': 'Gemini + Templates',
                'multi_model': 'Multi-Model Cascade',
                'style_aware': 'Style-Aware Generator',
                'simple': 'Pattern-Based'
            };
            return names[generator] || 'Unknown';
        }
        
        function displayContent(result) {
            currentContent = result;
            
            // Update metadata
            document.getElementById('modelUsed').textContent = result.model_used || 'Unknown';
            document.getElementById('templateUsed').textContent = result.template_used || 'Auto';
            document.getElementById('generationTime').textContent = result.generationTime || '-';
            
            const outputDiv = document.getElementById('generatedContent');
            outputDiv.innerHTML = '';
            
            if (result.content_type === 'thread' && Array.isArray(result.content)) {
                result.content.forEach((tweet, index) => {
                    outputDiv.appendChild(createTweetElement(tweet, index + 1, result.content.length));
                });
            } else {
                outputDiv.appendChild(createTweetElement(result.content));
            }
            
            // Show diagram if included
            if (result.diagram_path) {
                const diagramDiv = document.createElement('div');
                diagramDiv.className = 'tweet-card';
                diagramDiv.innerHTML = `
                    <h3>Generated Diagram</h3>
                    <img src="${result.diagram_path}" style="max-width: 100%; border-radius: 8px;">
                    <div class="tweet-actions" style="margin-top: 15px;">
                        <button class="action-btn" onclick="downloadDiagram('${result.diagram_path}')">
                            💾 Download
                        </button>
                    </div>
                `;
                outputDiv.appendChild(diagramDiv);
            }
            
            document.getElementById('output').style.display = 'block';
            
            // Update stats
            stats.total++;
            if (result.content_type === 'thread' && Array.isArray(result.content)) {
                stats.totalChars += result.content.reduce((sum, tweet) => sum + tweet.length, 0);
            } else {
                stats.totalChars += result.content.length;
            }
            saveStats();
        }
        
        function createTweetElement(content, position = null, total = null) {
            const tweetDiv = document.createElement('div');
            tweetDiv.className = 'tweet-card';
            
            const chars = content.length;
            let charClass = '';
            if (chars > 280) charClass = 'danger';
            else if (chars > 250) charClass = 'warning';
            
            tweetDiv.innerHTML = `
                <div class="tweet-header">
                    <span class="tweet-number">
                        ${position ? `Tweet ${position}${total ? '/' + total : ''}` : 'Single Tweet'}
                    </span>
                    <span class="char-count ${charClass}">${chars}/280</span>
                </div>
                <div class="tweet-content">${escapeHtml(content)}</div>
                <div class="tweet-actions">
                    <button class="action-btn" onclick="copyTweet('${escapeHtml(content).replace(/'/g, "\\'")}')">
                        📋 Copy
                    </button>
                    <button class="action-btn" onclick="editTweet(this, '${escapeHtml(content).replace(/'/g, "\\'")}')">
                        ✏️ Edit
                    </button>
                    <button class="action-btn" onclick="regenerateSingle()">
                        🔄 Regenerate
                    </button>
                    <button class="action-btn" onclick="saveTweet('${escapeHtml(content).replace(/'/g, "\\'")}')">
                        💾 Save
                    </button>
                    <button class="action-btn" onclick="postToTwitter('${escapeHtml(content).replace(/'/g, "\\'")}')">
                        🐦 Post
                    </button>
                </div>
            `;
            
            return tweetDiv;
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        function copyTweet(content) {
            navigator.clipboard.writeText(content);
            showToast('Copied to clipboard!', 'success');
        }
        
        function editTweet(button, originalContent) {
            const tweetCard = button.closest('.tweet-card');
            const contentDiv = tweetCard.querySelector('.tweet-content');
            
            contentDiv.innerHTML = `
                <textarea class="form-control" style="width: 100%; min-height: 100px;">${originalContent}</textarea>
                <div style="margin-top: 10px;">
                    <button class="btn btn-secondary btn-small" onclick="saveEdit(this)">Save</button>
                    <button class="btn btn-secondary btn-small" onclick="cancelEdit(this, '${originalContent.replace(/'/g, "\\'")}')">Cancel</button>
                </div>
            `;
        }
        
        function saveEdit(button) {
            const textarea = button.parentElement.parentElement.querySelector('textarea');
            const newContent = textarea.value;
            const tweetCard = button.closest('.tweet-card');
            
            // Update display
            tweetCard.querySelector('.tweet-content').textContent = newContent;
            
            // Update character count
            const charCount = tweetCard.querySelector('.char-count');
            const chars = newContent.length;
            charCount.textContent = `${chars}/280`;
            charCount.className = 'char-count';
            if (chars > 280) charCount.classList.add('danger');
            else if (chars > 250) charCount.classList.add('warning');
            
            // Recreate actions
            const actionsHtml = `
                <button class="action-btn" onclick="copyTweet('${newContent.replace(/'/g, "\\'")}')">
                    📋 Copy
                </button>
                <button class="action-btn" onclick="editTweet(this, '${newContent.replace(/'/g, "\\'")}')">
                    ✏️ Edit
                </button>
                <button class="action-btn" onclick="regenerateSingle()">
                    🔄 Regenerate
                </button>
                <button class="action-btn" onclick="saveTweet('${newContent.replace(/'/g, "\\'")}')">
                    💾 Save
                </button>
                <button class="action-btn" onclick="postToTwitter('${newContent.replace(/'/g, "\\'")}')">
                    🐦 Post
                </button>
            `;
            tweetCard.querySelector('.tweet-actions').innerHTML = actionsHtml;
            
            showToast('Edit saved!', 'success');
        }
        
        function cancelEdit(button, originalContent) {
            const tweetCard = button.closest('.tweet-card');
            tweetCard.querySelector('.tweet-content').textContent = originalContent;
        }
        
        function regenerateSingle() {
            document.getElementById('generateBtn').click();
        }
        
        async function saveTweet(content) {
            try {
                const response = await fetch('/save_tweet', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        content: content,
                        metadata: currentContent
                    })
                });
                
                if (response.ok) {
                    stats.saved++;
                    saveStats();
                    updateStats();
                    showToast('Tweet saved!', 'success');
                }
            } catch (error) {
                showToast('Error saving tweet', 'error');
            }
        }
        
        async function postToTwitter(content) {
            if (!confirm('Post this tweet to Twitter/X?')) return;
            
            try {
                const response = await fetch('/post_to_twitter', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({content: content})
                });
                
                const result = await response.json();
                if (result.success) {
                    showToast('Posted to Twitter!', 'success');
                } else {
                    showToast('Error: ' + result.error, 'error');
                }
            } catch (error) {
                showToast('Error posting to Twitter', 'error');
            }
        }
        
        function submitFeedback(score) {
            // Highlight selected feedback
            document.querySelectorAll('.feedback-btn').forEach(btn => {
                btn.classList.remove('selected');
            });
            event.target.classList.add('selected');
            
            // Store feedback score
            if (currentContent) {
                currentContent.feedbackScore = score;
            }
        }
        
        async function saveFeedback() {
            if (!currentContent) return;
            
            const details = document.getElementById('feedbackDetails').value;
            const feedbackData = {
                content: currentContent,
                score: currentContent.feedbackScore || 'not_rated',
                details: details,
                timestamp: new Date().toISOString()
            };
            
            try {
                const response = await fetch('/save_feedback', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(feedbackData)
                });
                
                if (response.ok) {
                    // Update stats
                    if (currentContent.feedbackScore) {
                        const scoreMap = {'great': 5, 'good': 4, 'okay': 3, 'needs_work': 2, 'poor': 1};
                        stats.feedbackScores.push(scoreMap[currentContent.feedbackScore] || 3);
                        saveStats();
                        updateStats();
                    }
                    
                    showToast('Feedback saved! Thank you!', 'success');
                    document.getElementById('feedbackDetails').value = '';
                }
            } catch (error) {
                showToast('Error saving feedback', 'error');
            }
        }
        
        function updateStats() {
            document.getElementById('totalGenerated').textContent = stats.total;
            document.getElementById('savedCount').textContent = stats.saved;
            
            // Calculate average score
            if (stats.feedbackScores.length > 0) {
                const avg = stats.feedbackScores.reduce((a, b) => a + b, 0) / stats.feedbackScores.length;
                document.getElementById('avgScore').textContent = avg.toFixed(1);
            }
        }
        
        function saveStats() {
            localStorage.setItem('tweetStats', JSON.stringify(stats));
        }
        
        function addToHistory(topic, result) {
            const historyItem = {
                topic: topic,
                content: result.content,
                timestamp: new Date().toISOString(),
                type: result.content_type
            };
            
            generationHistory.unshift(historyItem);
            if (generationHistory.length > 10) {
                generationHistory = generationHistory.slice(0, 10);
            }
            
            localStorage.setItem('tweetHistory', JSON.stringify(generationHistory));
            loadHistory();
        }
        
        function loadHistory() {
            const historyList = document.getElementById('historyList');
            historyList.innerHTML = '';
            
            generationHistory.forEach((item, index) => {
                const historyDiv = document.createElement('div');
                historyDiv.className = 'history-item';
                historyDiv.onclick = () => loadFromHistory(index);
                
                const preview = Array.isArray(item.content) ? item.content[0] : item.content;
                
                historyDiv.innerHTML = `
                    <div class="history-timestamp">${new Date(item.timestamp).toLocaleString()}</div>
                    <div class="history-preview">${item.topic}</div>
                `;
                
                historyList.appendChild(historyDiv);
            });
        }
        
        function loadFromHistory(index) {
            const item = generationHistory[index];
            document.getElementById('topic').value = item.topic;
            showToast('Topic loaded from history', 'success');
        }
        
        function showToast(message, type = 'success') {
            const toast = document.getElementById('toast');
            toast.textContent = message;
            toast.className = 'toast ' + type;
            toast.style.display = 'block';
            
            setTimeout(() => {
                toast.style.display = 'none';
            }, 3000);
        }
        
        async function downloadDiagram(path) {
            window.open(path, '_blank');
        }
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + Enter to generate
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                document.getElementById('generateBtn').click();
            }
            
            // Ctrl/Cmd + S to save
            if ((e.ctrlKey || e.metaKey) && e.key === 's') {
                e.preventDefault();
                if (currentContent) {
                    saveTweet(currentContent.content);
                }
            }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Render the main interface"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/generate_enhanced', methods=['POST'])
def generate_enhanced():
    """Enhanced content generation with all features"""
    data = request.json
    
    try:
        topic = data.get('topic', '')
        content_type = data.get('contentType', 'single')
        category = data.get('category', 'auto')
        tone = data.get('tone', 'explanatory')
        template = data.get('template', 'auto')
        context = data.get('context', '')
        generator_type = data.get('generator', 'unified')
        include_diagram = data.get('includeDiagram', False)
        include_links = data.get('includeLinks', True)
        auto_polish = data.get('autoPolish', True)
        
        # Select generator
        generator = generators.get(generator_type)
        if not generator:
            return jsonify({'error': f'Generator {generator_type} not available'})
        
        # Generate content based on type
        if generator_type == 'unified':
            result = generator.generate_tweet(
                topic=topic,
                template_name=template if template != 'auto' else None,
                context=context
            )
        elif generator_type == 'multi_model':
            result = generator.generate_tweet(
                topic=topic,
                content_type=content_type,
                tone=tone
            )
        elif generator_type == 'simple':
            if content_type == 'thread':
                result = generator.generate_thread(topic, category if category != 'auto' else None)
            else:
                result = generator.generate_single(topic, category if category != 'auto' else None)
        elif generator_type == 'style_aware':
            result = generator.generate_tweet(
                topic=topic,
                style=tone,
                include_links=include_links
            )
        
        # Format response
        response = {
            'content': result if isinstance(result, str) else result.get('content', ''),
            'content_type': content_type,
            'model_used': generator_type,
            'template_used': template,
            'category': category,
            'tone': tone
        }
        
        # Generate diagram if requested
        if include_diagram:
            diagram_path = generate_diagram(topic)
            if diagram_path:
                response['diagram_path'] = diagram_path
        
        # Add metadata
        response['timestamp'] = datetime.now().isoformat()
        response['character_count'] = len(response['content']) if isinstance(response['content'], str) else sum(len(t) for t in response['content'])
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/save_tweet', methods=['POST'])
def save_tweet():
    """Save generated tweet to file"""
    data = request.json
    
    try:
        # Create directory if it doesn't exist
        save_dir = Path('generated_tweets')
        save_dir.mkdir(exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = save_dir / f"tweet_{timestamp}.json"
        
        # Save content
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        return jsonify({'success': True, 'filename': str(filename)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/save_feedback', methods=['POST'])
def save_feedback():
    """Save user feedback"""
    data = request.json
    
    try:
        feedback_file = Path('feedback_log.json')
        
        # Load existing feedback
        if feedback_file.exists():
            with open(feedback_file, 'r') as f:
                feedback_history = json.load(f)
        else:
            feedback_history = []
        
        # Add new feedback
        feedback_history.append(data)
        
        # Save updated feedback
        with open(feedback_file, 'w') as f:
            json.dump(feedback_history, f, indent=2)
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/post_to_twitter', methods=['POST'])
def post_to_twitter():
    """Post content to Twitter (requires API credentials)"""
    data = request.json
    content = data.get('content', '')
    
    try:
        # Check if Twitter credentials are available
        if not all([os.environ.get(key) for key in ['API_KEY', 'API_SECRET', 'ACCESS_TOKEN', 'ACCESS_TOKEN_SECRET']]):
            return jsonify({'success': False, 'error': 'Twitter API credentials not configured'})
        
        # Use twitter_publisher.py
        result = subprocess.run(
            ['python', 'twitter_publisher.py', '--content', content],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': result.stderr})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/analytics')
def analytics():
    """Get analytics data"""
    try:
        # Load analytics
        analytics_file = Path('posts_analysis_detailed.json')
        if analytics_file.exists():
            with open(analytics_file, 'r') as f:
                analytics = json.load(f)
        else:
            analytics = {}
        
        # Load feedback data
        feedback_file = Path('feedback_log.json')
        if feedback_file.exists():
            with open(feedback_file, 'r') as f:
                feedback = json.load(f)
        else:
            feedback = []
        
        return jsonify({
            'analytics': analytics,
            'feedback': feedback
        })
    except Exception as e:
        return jsonify({'error': str(e)})

def generate_diagram(topic):
    """Generate a diagram for the topic using mermaid"""
    try:
        result = subprocess.run(
            ['python', 'mermaid_diagram_generator.py', topic],
            capture_output=True,
            text=True,
            cwd='/home/kushagra/X/XPosts'
        )
        
        if result.returncode == 0:
            # Extract diagram path from output
            output_lines = result.stdout.strip().split('\n')
            for line in output_lines:
                if 'generated_tweets/diagrams/' in line and '.png' in line:
                    return line.strip()
        
        return None
    except Exception:
        return None

if __name__ == "__main__":
    print("\n🚀 Enhanced Twitter/X Content Generator Web Interface")
    print("=" * 50)
    print("Starting on http://localhost:5000")
    print("=" * 50)
    
    # Run with production server settings
    from werkzeug.serving import run_simple
    run_simple('0.0.0.0', 5000, app, use_reloader=False, use_debugger=False)