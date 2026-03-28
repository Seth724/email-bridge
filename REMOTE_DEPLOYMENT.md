# Remote MCP Deployment - Interactive Buttons Guide

## Overview

When deployed to a **remote MCP server** (Railway, Render, Fly.io, etc.), the interactive buttons **work automatically** because:

✅ Your app has a public HTTPS URL  
✅ Telegram can reach your server  
✅ Webhook callbacks are received instantly  

## Quick Deploy to Railway

### Step 1: Install Railway CLI

```bash
npm install -g @railway/cli
```

### Step 2: Login to Railway

```bash
railway login
```

### Step 3: Initialize Railway Project

```bash
cd email-bridge
railway init
```

### Step 4: Add Environment Variables

```bash
# In Railway dashboard or CLI:
railway variables set GMAIL_ADDRESS=your@gmail.com
railway variables set GMAIL_APP_PASSWORD=your-app-password
railway variables set TELEGRAM_BOT_TOKEN=your-bot-token
railway variables set TELEGRAM_CHAT_ID=your-chat-id
railway variables set DEPLOYMENT_MODE=remote
railway variables set PUBLIC_URL=https://your-app.railway.app
```

### Step 5: Deploy

```bash
railway up
```

### Step 6: Get Your URL

```bash
railway domain
# Returns: https://email-bridge-production.up.railway.app
```

### Step 7: Register Webhook

```bash
# Option A: Auto-registered if DEPLOYMENT_MODE=remote and PUBLIC_URL set
# Option B: Manual registration
python webhook_setup.py set https://email-bridge-production.up.railway.app/webhook
```

### Step 8: Test Buttons

Send a test alert and click the buttons!

## Configuration for Different Platforms

### Railway

```json
// railway.json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python webhook_server.py",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE"
  }
}
```

Environment variables:
- `DEPLOYMENT_MODE=remote`
- `PUBLIC_URL=https://your-app.railway.app`
- `MCP_TRANSPORT=streamable-http` (for remote MCP)

### Render

```yaml
# render.yaml
services:
  - type: web
    name: email-bridge
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python webhook_server.py
    envVars:
      - key: DEPLOYMENT_MODE
        value: remote
      - key: PUBLIC_URL
        fromService:
          type: web
          name: email-bridge
          property: host
```

### Fly.io

```toml
# fly.toml
app = "email-bridge"

[build]
  dockerfile = "Dockerfile"

[env]
  DEPLOYMENT_MODE = "remote"
  PUBLIC_URL = "https://email-bridge.fly.dev"

[[services]]
  http_checks = [{ interval = 10000, path = "/health", method = "get" }]
  internal_port = 8000
  protocol = "tcp"
```

## How It Works When Deployed

```
┌─────────────────────────────────────────────────────────┐
│  Railway/Render Cloud                                   │
│                                                         │
│  ┌───────────────────────────────────────────────┐     │
│  │  Your Deployed App                            │     │
│  │  https://email-bridge.railway.app             │     │
│  │                                               │     │
│  │  ┌─────────────┐  ┌─────────────────────┐   │     │
│  │  │  MCP Server │  │  Webhook Server     │   │     │
│  │  │  (port 8000)│  │  (port 8000)        │   │     │
│  │  │             │  │                     │   │     │
│  │  │  - check_   │  │  POST /webhook      │   │     │
│  │  │  emails     │  │  - callback queries │   │     │
│  │  │             │  │  - button actions   │   │     │
│  │  └─────────────┘  └─────────────────────┘   │     │
│  └───────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────┘
           │                              │
           │ MCP Protocol                 │ Telegram Webhook
           │ (Claude Desktop)             │ (Button clicks)
           ▼                              ▼
    ┌──────────────┐              ┌──────────────┐
    │ Claude       │              │   Telegram   │
    │ Desktop      │              │   Servers    │
    └──────────────┘              └──────────────┘
```

## Testing After Deployment

### 1. Check Health Endpoint

```bash
curl https://email-bridge.railway.app/health
# Should return: {"status": "healthy"}
```

### 2. Check Webhook Status

```bash
python webhook_setup.py info
```

Expected output:
```json
{
  "url": "https://email-bridge.railway.app/webhook",
  "has_custom_certificate": false,
  "pending_update_count": 0
}
```

### 3. Send Test Alert

```bash
python -c "
from core.telegram import TelegramSender
import os
tg = TelegramSender(
    os.getenv('TELEGRAM_BOT_TOKEN'),
    os.getenv('TELEGRAM_CHAT_ID')
)
tg.send_urgent_alert_with_buttons(
    '🚨 Remote Deployment Test',
    'test_123',
    'Testing buttons on deployed server'
)
"
```

### 4. Click Buttons in Telegram

You should see:
- ✅ "Marked as read" (when clicking Mark as Read)
- 🗑️ "Archived" (when clicking Archive)
- 📋 Subject text (when clicking Copy Subject)

## Environment Variables for Remote Deploy

| Variable | Required | Example |
|----------|----------|---------|
| `GMAIL_ADDRESS` | ✅ | `you@gmail.com` |
| `GMAIL_APP_PASSWORD` | ✅ | `abcd1234efgh5678` |
| `TELEGRAM_BOT_TOKEN` | ✅ | `123456:ABC-DEF...` |
| `TELEGRAM_CHAT_ID` | ✅ | `7596520776` |
| `DEPLOYMENT_MODE` | ✅ | `remote` |
| `PUBLIC_URL` | ✅ | `https://app.railway.app` |
| `GROQ_API_KEY` | ✅ | `gsk_...` |
| `MCP_TRANSPORT` | Optional | `streamable-http` |

## Benefits of Remote Deployment

| Feature | Local | Remote Deploy |
|---------|-------|---------------|
| MCP tools | ✅ | ✅ |
| Voice summaries | ✅ | ✅ |
| Button display | ✅ | ✅ |
| **Button callbacks** | ❌ (needs ngrok) | ✅ **Works!** |
| Auto-webhook setup | ❌ | ✅ |
| 24/7 availability | ❌ | ✅ |
| Scheduled checks | ❌ (PC off) | ✅ |

## Troubleshooting

### Webhook not registering

Check logs for:
```
Auto-registered webhook: https://your-app.railway.app/webhook
```

If missing:
- Verify `DEPLOYMENT_MODE=remote`
- Verify `PUBLIC_URL` is set correctly
- Check Railway logs for errors

### Buttons don't respond

1. Check webhook is set:
   ```bash
   python webhook_setup.py info
   ```

2. Check `/webhook` endpoint is accessible:
   ```bash
   curl -X POST https://your-app.railway.app/webhook
   ```

3. Check Railway logs for incoming webhook requests

### MCP connection fails

- Ensure `MCP_TRANSPORT=streamable-http`
- Use SSE or streamable-http transport in Claude Desktop config
- Check firewall allows outbound connections

## Cost Estimate

| Platform | Free Tier | Paid (if needed) |
|----------|-----------|------------------|
| Railway | $5 credit/month | ~$5-10/month |
| Render | Free tier available | ~$7/month |
| Fly.io | Free allowance | ~$2-5/month |

**Total: ~$0-10/month** for 24/7 email bridge with working buttons!

## Next Steps

1. ✅ Deploy to Railway/Render
2. ✅ Set environment variables
3. ✅ Webhook auto-registers on startup
4. ✅ Test buttons in Telegram
5. ✅ Enjoy fully functional email notifications!

Questions? Check `WEBHOOK_README.md` for detailed webhook documentation.
