# 🚀 Deployment Guide

Complete guide for deploying Email Bridge to various platforms.

---

## 📋 Table of Contents

1. [GitHub Actions (Free, Recommended)](#github-actions-free-recommended)
2. [Railway (MCP Server + Automation)](#railway-mcp-server--automation)
3. [Render (Alternative to Railway)](#render-alternative-to-railway)
4. [Local Deployment](#local-deployment)
5. [Environment Variables Reference](#environment-variables-reference)

---

## GitHub Actions (Free, Recommended)

**Best for:** Personal automation (7 AM daily emails)

**Cost:** $0 (free for public repos or < 2000 minutes/month)

### Step 1: Push to GitHub

```bash
# Initialize git repo
git init
git add .
git commit -m "Initial commit: Email Bridge"

# Create repo on GitHub, then:
git remote add origin https://github.com/yourusername/email-bridge.git
git branch -M main
git push -u origin main
```

### Step 2: Add Secrets

Go to your GitHub repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Add these secrets:

| Secret Name | Value |
|-------------|-------|
| `GROQ_API_KEY` | Your Groq API key (from https://console.groq.com/) |
| `GMAIL_ADDRESS` | your.email@gmail.com |
| `GMAIL_APP_PASSWORD` | 16-char app password from Google |
| `TELEGRAM_BOT_TOKEN` | Bot token from @BotFather |
| `TELEGRAM_CHAT_ID` | Your Telegram chat ID |
| `LANGCHAIN_API_KEY` | (Optional) LangSmith API key |

### Step 3: Add Variables (Optional)

Go to **Variables** tab (same page as secrets)

| Variable Name | Value |
|---------------|-------|
| `GROQ_MODEL` | `llama-3.3-70b-versatile` |
| `LANGCHAIN_TRACING_V2` | `true` (or `false`) |
| `USE_CUSTOM_RULES` | `true` |

### Step 4: Test Workflow

1. Go to **Actions** tab
2. Click **"Daily Email Digest"** workflow
3. Click **"Run workflow"**
4. Wait 1-2 minutes
5. Check Telegram for message!

### Step 5: Schedule Works Automatically

The workflow runs every day at 7 AM UTC automatically!

**Change time:** Edit `.github/workflows/daily-digest.yml`:
```yaml
- cron: '0 7 * * *'  # Change to your timezone
# Use https://crontab.guru/ to convert
```

---

## Railway (MCP Server + Automation)

**Best for:** MCP server deployment + scheduled automation

**Cost:** $5/month credit (enough for personal use)

### Step 1: Install Railway CLI

```bash
npm install -g @railway/cli
```

### Step 2: Login to Railway

```bash
railway login
```

### Step 3: Initialize Project

```bash
cd email-bridge
railway init
```

Select:
- **New Project**: `email-bridge`
- **Deploy from**: GitHub repo (connect your GitHub)

### Step 4: Add Environment Variables

```bash
# Add all required variables
railway variables set GROQ_API_KEY=xxx
railway variables set GMAIL_ADDRESS=your.email@gmail.com
railway variables set GMAIL_APP_PASSWORD=xxxx
railway variables set TELEGRAM_BOT_TOKEN=xxx
railway variables set TELEGRAM_CHAT_ID=xxx
railway variables set LANGCHAIN_API_KEY=xxx
```

Or use the Railway dashboard: Project → Variables → Add Variable

### Step 5: Deploy

```bash
railway up
```

### Step 6: Get Your URL

```bash
railway domain
```

You'll get: `https://email-bridge-production.up.railway.app`

### Step 7: Add Cron Job (for 7 AM automation)

```bash
# Add cron service
railway cron add "0 7 * * *" "python standalone/bot.py"
```

### Step 8: Use MCP Server

Add to your AI client config:

**Claude Desktop:**
```json
{
  "mcpServers": {
    "email-bridge": {
      "url": "https://email-bridge-production.up.railway.app/sse"
    }
  }
}
```

**Cursor:**
Settings → MCP → Add Server → Paste URL

**Any MCP client:** Just add the URL!

---

## Render (Alternative to Railway)

**Best for:** Free tier hosting

**Cost:** Free (with limitations) or $7/month

### Step 1: Create Render Account

Go to https://render.com/ and sign up

### Step 2: Create New Web Service

1. Click **New +** → **Web Service**
2. Connect GitHub repo
3. Select your `email-bridge` repo

### Step 3: Configure

- **Name**: `email-bridge`
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python mcp/server.py --remote`

### Step 4: Add Environment Variables

In Render dashboard → Environment → Add Variable

Add all the same variables as Railway.

### Step 5: Deploy

Click **Create Web Service**

Wait 2-3 minutes for deployment.

### Step 6: Get URL

Your service URL: `https://email-bridge.onrender.com`

### Step 7: Add Cron Job (for automation)

1. Go to **Crons** tab
2. Click **New Cron Job**
3. Configure:
   - **Name**: Daily Digest
   - **Schedule**: `0 7 * * *`
   - **Command**: `python standalone/bot.py`
   - **Branch**: `main`

---

## Local Deployment

**Best for:** Testing, development

### Option 1: Run Once

```bash
python standalone/bot.py
```

### Option 2: Run Scheduler (7 AM daily)

```bash
python standalone/scheduler.py
```

**Keep this terminal open!** It will run in foreground.

### Option 3: Run MCP Server (Local)

```bash
python mcp/server.py
```

Add to `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "email-bridge": {
      "command": "python",
      "args": ["mcp/server.py"]
    }
  }
}
```

### Option 4: Windows Task Scheduler

1. Open **Task Scheduler**
2. **Create Basic Task**
3. Name: `Email Bridge Daily Digest`
4. Trigger: **Daily** at 7:00 AM
5. Action: **Start a program**
   - Program: `python.exe`
   - Arguments: `standalone\bot.py`
   - Start in: `D:\MetaruneLabs\mcp-server\email-bridge`

### Option 5: macOS/Linux Cron

```bash
crontab -e

# Add this line (runs at 7 AM daily)
0 7 * * * cd /path/to/email-bridge && /path/to/venv/bin/python standalone/bot.py
```

---

## Environment Variables Reference

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `GROQ_API_KEY` | Groq AI API key | `gsk_xxxxx` |
| `GMAIL_ADDRESS` | Your Gmail address | `user@gmail.com` |
| `GMAIL_APP_PASSWORD` | Gmail app password | `abcd-efgh-ijkl-mnop` |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token | `123456:ABC-DEF...` |
| `TELEGRAM_CHAT_ID` | Your Telegram chat ID | `123456789` |

### Optional Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | Groq model to use |
| `GMAIL_IMAP_SERVER` | `imap.gmail.com` | Gmail IMAP server |
| `GMAIL_IMAP_PORT` | `993` | IMAP port |
| `SCHEDULE_HOUR` | `7` | Hour for daily digest (24h format) |
| `SCHEDULE_MINUTE` | `0` | Minute for daily digest |
| `TIMEZONE` | `UTC` | Timezone for scheduler |
| `LANGCHAIN_API_KEY` | (empty) | LangSmith API key for tracing |
| `LANGCHAIN_TRACING_V2` | `false` | Enable LangSmith tracing |
| `LANGCHAIN_PROJECT` | `email-bridge` | LangSmith project name |
| `USE_CUSTOM_RULES` | `true` | Enable custom classification rules |

---

## MCP Server Deployment Comparison

| Platform | Cost | Setup Time | Always On? | Best For |
|----------|------|------------|------------|----------|
| **GitHub Actions** | Free | 10 min | ✅ (scheduled) | Personal automation |
| **Railway** | $5/mo | 15 min | ✅ | MCP server + automation |
| **Render** | Free/$7 | 20 min | ✅ (free has sleep) | Budget hosting |
| **Local** | Free | 5 min | ❌ (your PC) | Testing only |
| **VPS** | $5-10/mo | 30 min | ✅ | Full control |

---

## Quick Deploy Commands

### GitHub Actions
```bash
git init && git add . && git commit -m "init"
git remote add origin https://github.com/user/repo.git
git push -u origin main
# Add secrets on GitHub
```

### Railway
```bash
railway login
railway init
railway variables set GROQ_API_KEY=xxx GMAIL_ADDRESS=xxx ...
railway up
railway domain
railway cron add "0 7 * * *" "python standalone/bot.py"
```

### Render
```bash
# Deploy via web UI
# Add env vars in dashboard
# Create cron job in dashboard
```

---

## Testing Deployment

### Test GitHub Actions
```bash
# Go to Actions tab → Click workflow → Run workflow
# Check Telegram for message
```

### Test Railway/Render
```bash
# Get URL from railway domain or render dashboard
# Test MCP endpoint:
curl https://your-app.railway.app/health

# Add to AI client config and test:
# "Check my emails"
```

### Test Local
```bash
python standalone/bot.py
# Check Telegram for message
```

---

## Troubleshooting

### GitHub Actions Fails

**Problem:** "Permission denied" or "Secrets not found"

**Solution:**
1. Check secrets are added correctly (no extra spaces)
2. Make sure workflow has permissions:
   ```yaml
   permissions:
     contents: read
   ```

### Railway Deployment Fails

**Problem:** "Build failed" or "Health check failed"

**Solution:**
1. Check logs: `railway logs`
2. Verify all environment variables are set
3. Check `railway.json` is valid JSON

### MCP Server Not Connecting

**Problem:** AI client can't connect to MCP server

**Solution:**
1. Check server is running: `curl https://your-app.com/health`
2. Verify URL in config is correct
3. Check firewall allows inbound connections

### Telegram Messages Not Sending

**Problem:** Bot doesn't send messages

**Solution:**
1. Verify bot token is correct
2. Make sure you sent `/start` to the bot
3. Check chat ID is correct (use @userinfobot)

---

## Next Steps After Deployment

1. ✅ Test email check works
2. ✅ Verify 7 AM schedule runs
3. ✅ Test MCP server connection
4. ✅ Enable LangSmith tracing
5. ✅ Customize classification rules
6. ✅ Share with friends!

---

## Support

- **Documentation**: See [README.md](README.md)
- **Issues**: [GitHub Issues](https://github.com/yourusername/email-bridge/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/email-bridge/discussions)

**Happy deploying!** 🚀
