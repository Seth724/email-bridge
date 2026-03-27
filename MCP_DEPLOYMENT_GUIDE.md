# Email Bridge MCP Server - Deployment Guide

Deploy your own Email Bridge instance and connect it to Claude Desktop as an MCP server for intelligent email triage and instant Telegram notifications.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Deployment Methods](#deployment-methods)
4. [Setup Instructions](#setup-instructions)
5. [Connect to Claude Desktop](#connect-to-claude-desktop)
6. [Usage Examples](#usage-examples)
7. [Troubleshooting](#troubleshooting)

---

## Overview

Email Bridge is a **multi-user capable** MCP server that:
- ✅ Connects to your **personal Gmail account**
- 🤖 Uses **Groq AI** to classify emails (URGENT/IMPORTANT/NORMAL/SPAM)
- 💬 Sends notifications to **your Telegram account**
- 🧠 Integrates with **Claude AI** for intelligent email insights
- ⏰ Runs **automatically** on a schedule (optional)

**What you get:**
- Instant access to email summaries in Claude
- One-click email classification
- Urgent alerts sent to Telegram immediately
- Morning digest of all emails at 7 AM
- Custom classification rules

---

## Architecture

### How It Works

```
┌─────────────────────────────────────────────────────────┐
│                    USER'S GMAIL ACCOUNT                  │
│              (amanethmeis@gmail.com)                     │
└────────────────────┬────────────────────────────────────┘
                     │ IMAP Protocol
                     ▼
┌─────────────────────────────────────────────────────────┐
│              EMAIL BRIDGE MCP SERVER                      │
│  (Runs on your machine OR cloud server)                  │
│                                                           │
│  📧 Gmail Fetcher  →  🤖 Classifier  →  💬 Telegram     │
│     (IMAP)             (Groq AI)          Sender         │
└────────────────────┬────────────────────────────────────┘
                     │ MCP Protocol
        ┌────────────┼────────────┐
        ▼            ▼            ▼
    ┌────────┬──────────┬──────────┐
    │        │          │          │
   Claude  Telegram   Browser   Other
   Desktop   Chat                Tools
```

### Data Flow When Connected to Claude

```
1. User: "Check my urgent emails"
   ↓
2. Claude → MCP Server: check_emails()
   ↓
3. MCP Server:
   └─ Connects to Gmail via IMAP
   └─ Fetches unread emails
   └─ Classifies with Groq AI
   └─ Returns structured data
   ↓
4. Claude displays: "📧 You have 3 urgent emails..."
   ↓
5. User: "Send urgent to Telegram"
   ↓
6. Claude → MCP Server: send_telegram_message(message, urgent=true)
   ↓
7. User receives instant push notification on Telegram
```

---

## Deployment Methods

### Option 1: Local Machine (Recommended for Testing)
- **Runs on:** Your computer
- **Always on:** Only when your computer is on
- **Setup time:** 10 minutes
- **Cost:** $0.001 per classified email (Groq AI)
- **Best for:** Personal use, testing

### Option 2: Cloud Server (GitHub Actions)
- **Runs on:** GitHub's servers
- **Always on:** 24/7, automatically
- **Setup time:** 15 minutes
- **Cost:** Same as local
- **Best for:** Daily scheduled digests at 7 AM

### Option 3: Cloud Server (Railway/Render)
- **Runs on:** Railway.app or Render.com
- **Always on:** 24/7, always responsive
- **Setup time:** 20 minutes
- **Cost:** ~$0/month free tier (or $5/month paid)
- **Best for:** Always-on MCP server access from Claude

---

## Setup Instructions

### Prerequisites

Before you start, gather these credentials:

1. **Gmail App Password**
   - Go to [Google Account Security](https://myaccount.google.com/security)
   - Enable 2-Step Verification
   - Create App Password (select Mail + Windows Computer)
   - Copy the 16-character password

2. **Groq API Key**
   - Sign up at [console.groq.com](https://console.groq.com)
   - Create API key (free tier available)
   - Copy the key

3. **Telegram Bot Token + Chat ID**
   - Open Telegram, search for @BotFather
   - Create new bot: `/newbot`
   - Copy the HTTP API token
   - Start a direct message with your bot
   - Save your Chat ID (you can use `/getchatid` helper bot)

### Step 1: Get the Code

```bash
# Clone the repository
git clone https://github.com/Seth724/mcp-server.git
cd mcp-server/email-bridge

# Or if you're already here, just use the existing folder
```

### Step 2: Install Dependencies

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 3: Create `.env` File

Create a file named `.env` in the `email-bridge` folder with your credentials:

```env
# Gmail Configuration
GMAIL_ADDRESS=your-email@gmail.com
GMAIL_APP_PASSWORD=abcd efgh ijkl mnop  (16 characters from App Password)

# Groq AI Configuration
GROQ_API_KEY=gsk_your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile

# Telegram Configuration
TELEGRAM_BOT_TOKEN=123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghi
TELEGRAM_CHAT_ID=7596520776  (your personal Telegram user ID)

# Optional
LANGCHAIN_TRACING_V2=false
USE_CUSTOM_RULES=true
SCHEDULE_HOUR=7
SCHEDULE_MINUTE=0
```

**⚠️ SECURITY IMPORTANT:**
- `.env` file is ignored by git (.gitignore)
- **NEVER** commit `.env` to GitHub
- Keep these credentials secret
- Rotate keys if accidentally exposed

### Step 4: Test Local Setup

**Test single run:**
```bash
python standalone/bot.py
```

Expected output:
```
00:04:19 - Starting email check...
00:04:21 - Connected to Gmail
00:04:22 - Fetched 5 unread emails
00:04:27 - Classified: 5 emails
00:04:32 - Sent Telegram notification
```

**Test MCP server locally:**
```bash
python mcp/server.py
```

Expected output:
```
Email Bridge
Listening on stdio
Tools Available:
  - check_emails
  - get_urgent_summary
  - send_telegram_message
  - test_connection
```

---

## Connect to Claude Desktop

### Step 1: Configure Claude Desktop

**Windows:** Open `%APPDATA%\Claude\claude_desktop_config.json`

**Mac:** Open `~/Library/Application Support/Claude/claude_desktop_config.json`

Add this to the `mcpServers` section:

```json
{
  "mcpServers": {
    "email-bridge": {
      "command": "python",
      "args": [
        "C:\\Users\\YOUR_USERNAME\\Desktop\\email-bridge\\mcp\\server.py"
      ],
      "env": {
        "GMAIL_ADDRESS": "your-email@gmail.com",
        "GMAIL_APP_PASSWORD": "abcd efgh ijkl mnop",
        "GROQ_API_KEY": "gsk_...",
        "TELEGRAM_BOT_TOKEN": "123456789:ABC...",
        "TELEGRAM_CHAT_ID": "7596520776"
      }
    }
  }
}
```

**⚠️ Alternative (Recommended):** Use `.env` file instead:

```json
{
  "mcpServers": {
    "email-bridge": {
      "command": "python",
      "args": [
        "C:\\Users\\YOUR_USERNAME\\Desktop\\email-bridge\\mcp\\server.py"
      ],
      "cwd": "C:\\Users\\YOUR_USERNAME\\Desktop\\email-bridge"
    }
  }
}
```

(This way Claude reads from `.env` file, safer than hardcoding)

### Step 2: Restart Claude Desktop

- Close Claude completely
- Reopen Claude
- You should see "Email Bridge" with a checkmark in Tools

### Step 3: Test the Connection

In Claude, ask:

```
Test the Email Bridge connection to my Gmail and Telegram
```

Claude will call `test_connection()` tool. Expected response:

```
✅ Gmail: Connected (5 unread emails)
✅ Telegram: Connected (Bot active)
```

---

## Usage Examples

### Example 1: Check Emails in Claude

**You ask Claude:**
```
What urgent emails do I have today?
```

**Claude:**
1. Calls `check_emails()` tool
2. Gets classified emails from your Gmail
3. Filters for URGENT only
4. Shows you the summary

**Response:**
```
🚨 URGENT EMAILS (2):

1. Security Alert from Google
   Summary: Verify your account activity
   Action: Check your security dashboard

2. Password Reset from Microsoft
   Summary: Someone attempted to reset your password
   Action: Verify you authorized this change
```

### Example 2: Send Alert to Telegram from Claude

**You ask Claude:**
```
Send this important message to my Telegram: "Meeting moved to 3 PM"
```

**Claude:**
1. Calls `send_telegram_message()` tool
2. Sends message to your Telegram chat
3. You receive instant push notification on your phone

---

### Example 3: Generate Summary with Claude

**You ask Claude:**
```
Summarize my emails and highlight anything that needs immediate action
```

**Claude:**
1. Calls `check_emails()` tool
2. Gets all classified emails
3. Uses its reasoning to add insights
4. Shows you structured analysis with priorities

```
📊 TODAY'S EMAIL SUMMARY

⚠️ ISSUES REQUIRING ACTION (2):
- Security alerts from Google & Microsoft (likely spam or compromised password)
  → Recommendation: Reset passwords immediately

📌 IMPORTANT (3):
- Project updates from team
- Invoice notification
- Event reminder

✅ OK (2):
- Newsletter subscriptions
- Notifications

💡 AI Insight: The security alerts are suspicious. I recommend:
1. Reset all passwords
2. Enable 2FA on both Google and Microsoft
3. Check recent login activity
```

---

## Advanced: Scheduled Daily Digests

### Option A: GitHub Actions (Free, Cloud)

**Already configured!** Just add secrets to GitHub:

1. Go to GitHub repo → Settings → Secrets and Variables → Actions
2. Add secrets:
   - `GROQ_API_KEY`
   - `GMAIL_ADDRESS`
   - `GMAIL_APP_PASSWORD`
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`

3. Workflow runs automatically at 7 AM daily

**Check status:**
- Go to Actions tab
- See all runs and their logs

### Option B: Local Scheduler

Keep the MCP server + scheduler running on your computer:

```bash
# Run scheduler in background (Windows)
python standalone/scheduler.py &

# Or on Mac/Linux
python standalone/scheduler.py &
```

This runs daily at 7 AM and weekly summary on Sunday 8 PM.

### Option C: Railway.app (Cloud, Always-On)

1. Install Railway CLI: `npm install -g @railway/cli`
2. Login: `railway login`
3. Create project: `railway init`
4. Add variables to Railway dashboard (same env vars)
5. Deploy: `railway up`
6. Railway redeploys automatically on git push

---

## Troubleshooting

### MCP Server Won't Connect in Claude

**Problem:** Claude shows "tools unavailable" or won't load Email Bridge

**Solutions:**
1. Check the path in `claude_desktop_config.json` is correct
2. Test MCP server locally: `python mcp/server.py`
3. Verify Python is in PATH: `python --version`
4. Check `.env` file exists and has all variables
5. Restart Claude completely

### Gmail Connection Fails

**Problem:** "Failed to connect to Gmail" error

**Solutions:**
1. Verify Gmail app password (16 chars with spaces) is exactly correct
2. Enable 2-Step Verification on Google Account
3. Create a NEW app password (don't reuse old ones)
4. Check Gmail address is spelled correctly
5. Try test: `python -c "from core.gmail import GmailFetcher; GmailFetcher(...)"`

### Telegram Not Receiving Messages

**Problem:** "Failed to send Telegram message"

**Solutions:**
1. Verify bot token is correct (from @BotFather)
2. Verify chat ID is correct (from `/getchatid` bot)
3. Start a message with your bot first: `@YourBotName /start`
4. Check bot is not restricted by Telegram
5. Try test: `python -c "from core.telegram import TelegramSender; TelegramSender(...).send_message('test')"`

### Groq API Fails

**Problem:** "Failed to classify email" or API errors

**Solutions:**
1. Verify Groq API key is correct (from console.groq.com)
2. Check free tier not exceeded (high email volume + free plan limit)
3. Verify model name: `llama-3.3-70b-versatile`
4. Try test: `python -c "from core.classifier import EmailClassifier; EmailClassifier(...)"`

### Too Many Classifications (Cost)

**Each email costs ~$0.001** with Groq API.

**Ways to reduce costs:**
1. Enable custom rules in `config/rules.ini`
   - Match common emails to avoid AI call
   - Saves ~$0.001 per matched email

2. Use `get_urgent_summary()` instead of full `check_emails()`
   - Only classifies urgent, skips others

3. Request fewer emails: `check_emails(limit=5, days_back=1)`

---

## Multi-User Deployment (Enterprise)

If you want **multiple users** to connect to the same instance:

### Architecture Needed

```
MCP Server (Shared)
  ├─ User 1 (own Gmail, own Telegram)
  ├─ User 2 (own Gmail, own Telegram)
  └─ User 3 (own Gmail, own Telegram)
```

### Implementation

Currently, Email Bridge uses **one set of credentials per deployment**.

For multi-user, you'd need:

1. **User Database**
   - Store each user's Gmail + Telegram credentials

2. **Modified MCP Tools**
   - Accept `user_id` parameter
   - Look up that user's credentials
   - Call Gmail/Telegram with their tokens

3. **Example modified tool:**
```python
@mcp.tool()
def check_emails(user_id: str, limit: int = 10) -> dict:
    """Check emails for a specific user"""
    user = db.get_user(user_id)  # Database lookup
    
    gmail = GmailFetcher(
        email_address=user["gmail"],
        app_password=user["app_password"]
    )
    # ... rest of logic
```

4. **Shared MCP Server URL**
   - Deploy on Railway/Render
   - Configure in Claude: `command: curl` or HTTP endpoint
   - All users connect to same server

**Would you like me to implement multi-user support?** It requires:
- SQLite database creation
- Modified tool signatures
- User authentication layer

---

## Summary

### Single User (Current Setup)
✅ Works today
✅ Email Bridge connects to YOUR Gmail
✅ Claude Desktop reads YOUR emails
✅ Instant Telegram alerts for YOUR account

### Multi-User (Optional Future)
⏳ Not implemented yet
🔧 Requires database + code refactoring
💼 Suitable for teams/organizations

### Next Steps

1. **Test locally:** `python standalone/bot.py`
2. **Connect to Claude:** Edit `claude_desktop_config.json`
3. **Set up daily digest:** Add GitHub secrets
4. **Enjoy!** Ask Claude about your emails

Questions? Check logs: `logs/email_bridge.log`

