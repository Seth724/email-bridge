# 🎨 Render Deployment Guide

## Free Tier Limits

- **500 hours/month** of web service runtime (enough for 24/7)
- **100GB bandwidth/month**
- **Shared CPU, 512MB RAM**
- **Auto-sleep after 15 min inactivity** (wakes on request)

**Perfect for Email Bridge!** ✅

---

## Method 1: Deploy from GitHub (Recommended)

### Step 1: Push to GitHub

```bash
# Initialize git if not already
cd D:\MetaruneLabs\mcp-server\email-bridge
git init
git add .
git commit -m "Initial commit - Email Bridge"

# Create repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/email-bridge.git
git push -u origin main
```

### Step 2: Create Render Account

1. Go to: https://render.com
2. Click **Get Started for Free**
3. Sign up with GitHub (easiest) or email

### Step 3: Create New Web Service

1. Click **New +** → **Web Service**
2. Connect your GitHub account
3. Select your `email-bridge` repository
4. Render auto-detects `render.yaml`

### Step 4: Configure Service

**Settings:**
- **Name**: `email-bridge`
- **Region**: Choose closest to you (e.g., Oregon, Frankfurt)
- **Branch**: `main`
- **Root Directory**: (leave blank)
- **Runtime**: `Python`
- **Build Command**: `pip install -r requirements.txt && pip install -r requirements-audio.txt`
- **Start Command**: `python webhook_server.py`
- **Instance Type**: **Free**

### Step 5: Add Environment Variables

In Render dashboard, go to **Environment** tab and add:

```
GMAIL_ADDRESS = your.email@gmail.com
GMAIL_APP_PASSWORD = your16characterpassword
TELEGRAM_BOT_TOKEN = 123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
TELEGRAM_CHAT_ID = 7596520776
GROQ_API_KEY = gsk_xxxxxxxxxxxxxxxxxxxx
DEPLOYMENT_MODE = remote
PUBLIC_URL = https://email-bridge.onrender.com
PORT = 8000
```

Click **Save Changes**

### Step 6: Deploy

1. Go to **Manual Deploy** section
2. Select `main` branch
3. Click **Deploy**

Wait 2-5 minutes for build and deploy.

### Step 7: Get Your URL

After deploy completes, copy your URL:
```
https://email-bridge.onrender.com
```

### Step 8: Update PUBLIC_URL

1. Go to **Environment** tab
2. Update `PUBLIC_URL` with your actual URL
3. Click **Save Changes**
4. Redeploy (auto-triggers on save)

### Step 9: Check Logs

Go to **Logs** tab. Look for:
```
Auto-registered webhook: https://email-bridge.onrender.com/webhook
INFO:     Started server process
```

### Step 10: Test Health

```bash
curl https://email-bridge.onrender.com/health
```

Expected:
```json
{"status": "healthy", "service": "email-bridge-webhook"}
```

---

## Method 2: Deploy from Render Dashboard (No Git)

### Step 1: Create New Web Service

1. Go to https://dashboard.render.com
2. Click **New +** → **Web Service**
3. Select **Deploy from Git Repository** or **Deploy from Dockerfile**

### Step 2: Connect Repository

- Choose **GitHub** or **GitLab**
- Select your `email-bridge` repo

OR

- Use **Public Git Repository** and paste URL

### Step 3-10: Same as Method 1

Follow steps 4-10 from Method 1 above.

---

## Configure Claude Desktop for Render MCP

### Find Claude Desktop Config

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

**Mac:**
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

### Edit Config

```json
{
  "mcpServers": {
    "email-bridge": {
      "url": "https://email-bridge.onrender.com/sse"
    }
  }
}
```

Or with streamable-http (FastMCP v3):

```json
{
  "mcpServers": {
    "email-bridge": {
      "url": "https://email-bridge.onrender.com/mcp"
    }
  }
}
```

### Restart Claude Desktop

Close and reopen Claude Desktop.

---

## Test Your Deployment

### 1. Check Webhook Status

```bash
cd D:\MetaruneLabs\mcp-server\email-bridge
python webhook_setup.py info
```

Expected:
```json
{
  "url": "https://email-bridge.onrender.com/webhook",
  "has_custom_certificate": false
}
```

### 2. Send Test Alert with Buttons

```bash
python -c "from dotenv import load_dotenv; load_dotenv(); from core.telegram import TelegramSender; import os; tg = TelegramSender(os.getenv('TELEGRAM_BOT_TOKEN'), os.getenv('TELEGRAM_CHAT_ID')); tg.send_urgent_alert_with_buttons('🚨 RENDER TEST\n\nButtons should work!', 'test_123', 'Render Deployment Test')"
```

### 3. Click Buttons in Telegram

You should see confirmations:
- ✅ "Marked as read"
- 🗑️ "Archived"
- 📋 Subject text

---

## Using Your Deployed MCP

### In Claude Desktop:

**Check emails:**
```
Check my emails
```

**Send voice summary:**
```
Send voice summary of my emails
```

**Get urgent only:**
```
Any urgent emails?
```

**Send Telegram message:**
```
Send to Telegram: "Meeting starts in 5 minutes"
```

**Test connection:**
```
Test the email bridge connection
```

---

## Troubleshooting

### Service Won't Start

**Check Logs:**
```
Dashboard → Logs → See errors
```

**Common Issues:**
- Missing environment variables
- Typo in requirements.txt
- Port not set to 8000

### Webhook Not Registering

**Check logs for:**
```
Auto-registered webhook
```

**If missing:**
1. Verify `DEPLOYMENT_MODE=remote`
2. Verify `PUBLIC_URL` is correct
3. Manually register:
   ```bash
   python webhook_setup.py set https://email-bridge.onrender.com
   ```

### Service Goes to Sleep

Render free tier **sleeps after 15 min** of inactivity.

**Solutions:**

**Option 1: Keep Awake (Recommended)**
Use a free uptime monitor to ping your service:

1. Go to https://uptimerobot.com
2. Create free account
3. Add monitor: `https://email-bridge.onrender.com/health`
4. Set interval: 5 minutes

**Option 2: Accept Sleep**
- First request after sleep takes ~30 seconds
- Subsequent requests are fast
- Works fine for occasional use

### Claude Desktop Can't Connect

1. **Test URL in browser:**
   ```
   https://email-bridge.onrender.com/health
   ```

2. **Check Render logs** for incoming requests

3. **Try different transport:**
   - SSE: `https://email-bridge.onrender.com/sse`
   - HTTP: `https://email-bridge.onrender.com/mcp`

### Buttons Don't Work

1. Verify webhook is set: `python webhook_setup.py info`
2. Check URL matches your Render URL exactly
3. Check logs for incoming webhook requests
4. Ensure `DEPLOYMENT_MODE=remote` is set

---

## Monitoring

### Render Dashboard

- **Logs**: Real-time logs
- **Metrics**: CPU, memory, bandwidth
- **Deploys**: Deploy history

### Set Up Alerts (Optional)

1. Go to **Settings** → **Notifications**
2. Add email for deploy failures
3. Add email for service down

---

## Cost Estimate

| Resource | Free Tier | Your Usage | Cost |
|----------|-----------|------------|------|
| Render | 500 hrs/month | ~720 hrs (24/7) | $0* |
| Groq API | 500 req/day | ~100/day | $0 |
| Telegram | Unlimited | Unlimited | $0 |
| Gmail | Unlimited | Unlimited | $0 |

**Total: $0/month**

*Render rounds up to 500 hours for billing, so 24/7 usage = ~$0-7/month depending on exact hours

---

## Quick Reference

### Render Dashboard
https://dashboard.render.com

### Your Service URL
```
https://email-bridge.onrender.com
```

### Health Check
```bash
curl https://email-bridge.onrender.com/health
```

### Webhook Info
```bash
python webhook_setup.py info
```

### View Logs
```
Render Dashboard → Logs
```

### Redeploy
```
Render Dashboard → Manual Deploy → Deploy
```

### Environment Variables
```
Render Dashboard → Environment
```

---

## Next Steps

✅ Deploy to Render  
✅ Set all environment variables  
✅ Verify webhook auto-registers  
✅ Configure Claude Desktop  
✅ Test buttons in Telegram  
✅ Use MCP tools daily  

**You're all set!** 🎉

For detailed webhook docs, see `WEBHOOK_README.md`.
