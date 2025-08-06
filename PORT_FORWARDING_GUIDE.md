# 🌐 Windows Port Forwarding Guide for Tweet Generator

## Quick Start

### Step 1: Start the Web Server (on remote server)
```bash
cd /home/kushagra/X/XPosts
./start_web_server.sh
```

### Step 2: Set Up Port Forwarding (on Windows)

You have 3 options:

## Option 1: SSH with Port Forwarding (Recommended)

If you haven't connected yet, use this command in Windows Terminal/PowerShell:

```bash
ssh -L 5000:localhost:5000 kushagra@your-server-ip
```

This connects to your server AND forwards port 5000.

## Option 2: Add Port Forwarding to Existing Connection

If you're already connected via SSH, open a **new** Windows Terminal and run:

```bash
ssh -N -L 5000:localhost:5000 kushagra@your-server-ip
```

The `-N` flag means "just forward ports, don't open a shell"

## Option 3: Using VSCode Remote SSH

If you're using VSCode Remote SSH:

1. Press `F1` or `Ctrl+Shift+P`
2. Type "Forward a Port"
3. Enter `5000` when prompted
4. VSCode will handle the forwarding automatically

## Step 3: Access the Web Interface

Open your Windows browser and go to:
```
http://localhost:5000
```

## 🎯 What You'll See

A clean web interface where you can:
- Enter topics for tweet generation
- Choose between single tweets or threads
- Select specific templates (Problem/Solution, Deep Dive, Tools)
- Copy generated content with one click
- See generation statistics

## 🔧 Troubleshooting

### "Connection Refused" Error
- Make sure the web server is running on the remote server
- Check if port 5000 is already in use: `lsof -i :5000`
- Try a different port: Edit `web_interface.py` and change `port=5000` to `port=8080`

### "Flask not installed" Error
Install Flask on the remote server:
```bash
pip3 install flask --user
```

### Can't access localhost:5000 in browser
1. Verify port forwarding is active
2. Check Windows Firewall isn't blocking
3. Try `http://127.0.0.1:5000` instead

## 🚀 Advanced Setup

### Running in Background
Use tmux or screen to keep the server running:
```bash
tmux new -s tweet-gen
./start_web_server.sh
# Press Ctrl+B then D to detach
```

To reattach:
```bash
tmux attach -t tweet-gen
```

### Custom Port
To use a different port (e.g., 8080):
1. Edit `web_interface.py` - change `port=5000` to `port=8080`
2. Update your SSH forwarding: `-L 8080:localhost:8080`
3. Access at: `http://localhost:8080`

## 📱 Features of the Web Interface

1. **Topic Input**: Enter any technical topic
2. **Content Type**: Single tweet or multi-tweet thread
3. **Template Selection**: 
   - Auto-select based on context
   - Problem/Solution (Build in Public)
   - Conceptual Deep Dive
   - Workflow/Tools Share
4. **Context Field**: Add specific details like "problem: Docker failing in CI"
5. **Generator Type**: Style-aware (follows guide) or Simple pattern-based
6. **One-Click Actions**: Copy to clipboard, Regenerate
7. **Live Statistics**: Track total generated, average length, templates used

## 🎨 Example Usage

1. **For a debugging story**:
   - Topic: "Docker container debugging"
   - Template: "Problem/Solution"
   - Context: "problem: containers work locally but fail in CI, solution: fixed environment variables"

2. **For a tutorial**:
   - Topic: "How diffusion models work"
   - Template: "Conceptual Deep Dive"
   - Content Type: "Thread"

3. **For sharing tools**:
   - Topic: "Terminal productivity tools"
   - Template: "Workflow/Tools Share"
   - Context: "tools: tmux, fzf, jq"

The web interface makes it easy to generate, review, and copy content without dealing with command-line interfaces!