# Windows Setup Guide - Twitter/X Content Generator

This guide helps you access the Twitter/X Content Generator running on a remote server through your Windows browser.

## 🚀 Quick Start

### Step 1: Start the Server (on Remote Machine)

SSH into your remote server and run:

```bash
cd /home/kushagra/X/XPosts
./start_full_server.sh
```

Keep this terminal running - don't close it!

### Step 2: Set Up Port Forwarding (on Windows)

Open a **NEW** WSL terminal on your Windows machine and run ONE of these options:

#### Option A: New SSH Connection with Port Forwarding
```bash
ssh -L 5000:localhost:5000 kushagra@your-server-ip
```

#### Option B: If Already Connected via SSH
Open a NEW terminal (don't close your existing SSH session) and run:
```bash
ssh -N -L 5000:localhost:5000 kushagra@your-server-ip
```
(The `-N` flag means "don't execute commands, just forward ports")

#### Option C: For PowerShell Users
```powershell
ssh -L 5000:localhost:5000 kushagra@your-server-ip
```

### Step 3: Access in Browser

Open your Windows browser and go to:
```
http://localhost:5000
```

## 📋 Full Feature Access

The web interface provides access to all phases:

### Phase 1-2: Content Generation
- Generate tweets using multiple AI models (Gemini, Claude, OpenAI)
- Style-aware generation with templates
- Category-based content (Docker, AI Agents, DevTools, etc.)

### Phase 3: Diagram Generation
- Automatic Mermaid diagram creation
- Visual content for technical tweets

### Phase 4: Twitter Publishing
- Direct posting to Twitter/X (requires API credentials)
- Thread creation with media attachments

## 🔧 Troubleshooting

### "Connection Refused" Error
1. Make sure the server is running on the remote machine
2. Check if port 5000 is already in use:
   ```bash
   # On remote server
   lsof -i:5000
   ```
3. Kill any existing processes:
   ```bash
   # On remote server
   sudo kill -9 $(lsof -t -i:5000)
   ```

### "Port Already in Use" on Windows
1. Check what's using port 5000:
   ```cmd
   netstat -ano | findstr :5000
   ```
2. Use a different port:
   ```bash
   ssh -L 5001:localhost:5000 kushagra@your-server-ip
   ```
   Then access: http://localhost:5001

### SSH Connection Issues
1. Verify you can SSH normally:
   ```bash
   ssh kushagra@your-server-ip
   ```
2. Check your SSH config file (`~/.ssh/config`)
3. Try with verbose mode:
   ```bash
   ssh -v -L 5000:localhost:5000 kushagra@your-server-ip
   ```

## 🛡️ Security Notes

- Port forwarding is secure - traffic is encrypted through SSH
- Only your local machine can access localhost:5000
- The remote server port is not exposed to the internet

## 🎯 Advanced Usage

### Multiple Port Forwarding
If you need access to multiple services:
```bash
ssh -L 5000:localhost:5000 -L 5001:localhost:5001 -L 8080:localhost:8080 kushagra@your-server-ip
```

### Persistent Connection
To keep the connection alive:
```bash
ssh -o ServerAliveInterval=60 -L 5000:localhost:5000 kushagra@your-server-ip
```

### Using SSH Config
Add to `~/.ssh/config`:
```
Host tweet-server
    HostName your-server-ip
    User kushagra
    LocalForward 5000 localhost:5000
    ServerAliveInterval 60
```

Then simply: `ssh tweet-server`

## 📱 Using the Web Interface

Once connected, you'll see:

1. **Topic Input**: Enter your tweet topic
2. **Generate Button**: Create content
3. **Preview**: See generated tweets
4. **Save Options**: Export as JSON
5. **Diagram Integration**: Automatic diagram suggestions
6. **Publish Options**: Direct posting to Twitter (if configured)

## 🔍 Checking Server Status

From Windows WSL, test the connection:
```bash
curl http://localhost:5000
```

Should return HTML content if working correctly.

## 💡 Tips

1. **Keep terminals separate**: One for the server, one for port forwarding
2. **Use tmux/screen**: On the server to keep sessions alive
3. **Save your work**: Generated content is saved in `generated_tweets/`
4. **API Keys**: Configure in `config.json` on the server

## 📞 Need Help?

1. Check server logs in the terminal where you started the server
2. Verify all dependencies are installed
3. Ensure API keys are properly configured
4. Check the firewall isn't blocking connections

Remember: The server runs on the remote machine, but you access it through your local Windows browser via SSH port forwarding!