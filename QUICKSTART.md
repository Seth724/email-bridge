# 🚀 Quick Start Guide

## 5-Minute Setup

### Step 1: Get Your API Keys (5 minutes)

#### 1. Groq API Key (Free)
1. Visit: https://console.groq.com/
2. Sign up / Log in
3. Click "Create API Key"
4. Copy the key (starts with `gsk_...`)

#### 2. Gmail App Password (2 minutes)
1. Go to: https://myaccount.google.com/apppasswords
2. Select "Mail" and your device
3. Click "Generate"
4. Copy the 16-character password

#### 3. Telegram Bot Token (3 minutes)
1. Open Telegram, search for `@BotFather`
2. Send `/newbot`
3. Name your bot (e.g., "My Email Assistant")
4. Copy the token (starts with `123456:...`)

#### 4. Get Your Chat ID (1 minute)
1. Start a chat with your new bot
2. Visit: `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
3. Find `"chat":{"id":123456789}` in the response
4. Copy the number

---

### Step 2: Install and Configure (2 minutes)

```bash
# Clone or download this repository
cd email-bridge

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
copy .env.example .env   # Windows
# or
cp .env.example .env     # Mac/Linux
```

---

### Step 3: Edit .env File (1 minute)

Open `.env` and fill in your credentials:

```bash
GROQ_API_KEY=gsk_your-key-here
GROQ_MODEL=llama-3.3-70b-versatile

GMAIL_ADDRESS=your.email@gmail.com
GMAIL_APP_PASSWORD=abcd-efgh-ijkl-mnop

TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
TELEGRAM_CHAT_ID=123456789
```

---

### Step 4: Test It! (1 minute)

```bash
# Run one-time email check
python standalone/bot.py
```

You should receive a Telegram message with your email summary!

---

## 📅 Set Up Automation

### Option A: Run Scheduler Locally

```bash
# Runs every day at 7 AM (configurable)
python standalone/scheduler.py
```

Keep this running in the background. Press Ctrl+C to stop.

### Option B: GitHub Actions (Free, No Server Needed)

1. Go to your GitHub repo Settings → Secrets and variables → Actions
2. Add these secrets:
   - `GROQ_API_KEY`
   - `GMAIL_ADDRESS`
   - `GMAIL_APP_PASSWORD`
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`

3. The workflow runs automatically at 7 AM UTC daily!

### Option C: Deploy to Railway (24/7 Cloud)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Add environment variables
railway variables set GROQ_API_KEY=xxx GMAIL_ADDRESS=xxx ...

# Deploy
railway up

# Add cron job (7 AM daily)
railway cron add "0 7 * * *" "python standalone/bot.py"
```

---

## 🎯 Usage Examples

### Manual Email Check
```bash
python standalone/bot.py
```

### Run Scheduler (7 AM daily)
```bash
python standalone/scheduler.py
```

### Run MCP Server (for Claude Desktop)
```bash
python mcp/server.py
```

---

## 🔧 Troubleshooting

### "GROQ_API_KEY not set"
- Make sure `.env` file exists in the project directory
- Check that `GROQ_API_KEY` line is not commented out

### "Failed to connect to Gmail"
- Use **App Password**, not your regular Gmail password
- Enable 2FA on your Google account first
- Make sure IMAP is enabled in Gmail settings

### "Telegram message failed"
- Check that bot token is correct (no extra spaces)
- Make sure you started a chat with your bot (send `/start`)
- Verify chat ID is a number (not the username)

### "No unread emails found"
- The bot only checks **unread** emails from the **last 24 hours**
- Mark some emails as unread to test

---

## 📱 Telegram Commands

Once running, your bot supports:

- **Automatic**: Daily digest at 7 AM
- **Urgent alerts**: Instant notification for important emails
- **Manual trigger**: Coming soon (reply with `/check`)

---

## 🎓 Next Steps

1. **Customize classification**: Edit `core/classifier.py` prompts
2. **Change schedule**: Edit `SCHEDULE_HOUR` in `.env`
3. **Add more features**: Check out the code structure in README.md
4. **Deploy to cloud**: Follow Railway/Render deployment guides

---

## 📞 Need Help?

- **Documentation**: See [README.md](README.md)
- **Issues**: [Create GitHub issue](https://github.com/yourusername/email-bridge/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/email-bridge/discussions)

---

**Enjoy your intelligent inbox!** 🎉
