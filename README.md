# 📧 Email Bridge - Intelligent Inbox to Telegram

An AI-powered email triage system that monitors your Gmail and sends intelligent summaries to Telegram.

## 🎯 What It Does

- **Monitors Gmail** via IMAP (simple app password, no OAuth hassle)
- **Classifies emails** using Groq AI (Llama 3.3, Mixtral, or Gemma)
- **Sends summaries** to Telegram at 7 AM daily (or your preferred time)
- **Three deployment modes**: Standalone Bot, Local MCP, Remote MCP

## 🚀 Quick Start

### Option 1: Standalone Telegram Bot (Recommended for Most Users)

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/email-bridge.git
cd email-bridge

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment variables
cp .env.example .env
# Edit .env with your credentials

# 4. Run the bot
python standalone/bot.py

# 5. For scheduled automation (7 AM daily)
python standalone/scheduler.py
```

### Option 2: Local MCP Server (For Claude Desktop Users)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Add to claude_desktop_config.json
{
  "mcpServers": {
    "email-bridge": {
      "command": "python",
      "args": ["mcp/server.py"],
      "env": {
        "GROQ_API_KEY": "your-key",
        "GMAIL_ADDRESS": "your@email.com",
        "GMAIL_APP_PASSWORD": "your-app-password",
        "TELEGRAM_BOT_TOKEN": "your-token",
        "TELEGRAM_CHAT_ID": "your-chat-id"
      }
    }
  }
}

# 3. Restart Claude Desktop
# Now you can ask: "Check my important emails"
```

### Option 3: Remote MCP Server (Hosted on Railway/Render)

```bash
# 1. Deploy to Railway
railway init
railway up

# 2. Users add your URL to their AI client
{
  "mcpServers": {
    "email-bridge": {
      "url": "https://your-app.railway.app/sse"
    }
  }
}
```

## 📋 Configuration

### 1. Get Gmail App Password

1. Go to [Google Account Settings](https://myaccount.google.com/)
2. Security → 2-Step Verification → App Passwords
3. Generate password for "Mail"
4. Copy the 16-character password

### 2. Create Telegram Bot

1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot`
3. Follow prompts to name your bot
4. Copy the bot token

### 3. Get Your Chat ID

1. Start a chat with your new bot
2. Visit: `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
3. Find your `chat.id` in the response

### 4. Get Groq API Key

1. Visit [Groq Console](https://console.groq.com/)
2. Sign up / Log in
3. Create API Key
4. Copy the key

## 🔧 Environment Variables

```bash
# .env file

# Groq AI (Free tier: 500 requests/day)
GROQ_API_KEY=your-groq-api-key
GROQ_MODEL=llama-3.3-70b-versatile  # or mixtral-8x7b-32768, gemma2-9b-it

# Gmail IMAP
GMAIL_ADDRESS=your.email@gmail.com
GMAIL_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx
GMAIL_IMAP_SERVER=imap.gmail.com
GMAIL_IMAP_PORT=993

# Telegram Bot
TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
TELEGRAM_CHAT_ID=123456789

# Schedule (optional, default: 7 AM)
SCHEDULE_HOUR=7
SCHEDULE_MINUTE=0
TIMEZONE=UTC

# LangSmith (optional, for tracing)
LANGCHAIN_API_KEY=your-langsmith-key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=email-bridge
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│              EMAIL BRIDGE SYSTEM                     │
│                                                      │
│  ┌──────────────┐    ┌──────────────┐    ┌────────┐ │
│  │   Gmail      │ →  │   LangGraph  │ →  │Telegram│ │
│  │   IMAP       │    │  Classifier  │    │ Sender │ │
│  └──────────────┘    └──────────────┘    └────────┘ │
│         ↑                   ↑                  ↑     │
│    (App Password)      (Groq API)        (Bot API)   │
└─────────────────────────────────────────────────────┘
                          ↓
                   ┌──────────────┐
                   │  LangSmith   │
                   │  (Optional)  │
                   └──────────────┘
```

## 📂 Project Structure

```
email-bridge/
├── core/
│   ├── __init__.py
│   ├── gmail.py           # IMAP email fetcher
│   ├── classifier.py      # Groq AI classification
│   └── telegram.py        # Telegram sender
│
├── standalone/
│   ├── bot.py             # Simple Telegram bot
│   └── scheduler.py       # APScheduler for automation
│
├── mcp/
│   └── server.py          # FastMCP server
│
├── workflows/
│   └── triage_graph.py    # LangGraph workflow
│
├── .env.example
├── requirements.txt
└── README.md
```

## 🤖 Email Classification

The system classifies emails into 4 categories:

| Category | Action | Example |
|----------|--------|---------|
| **URGENT** | Immediate Telegram alert | Flight delays, job offers, bank alerts |
| **IMPORTANT** | Include in 7 AM digest | Meeting invites, project updates |
| **NORMAL** | Skip (regular email) | Newsletters, notifications |
| **SPAM** | Ignore | Promotional spam, phishing |

## 🎯 Use Cases

### For Job Seekers
> "🚨 New email from recruiter: 'Interview Request - Senior Dev @ Google'"

### For Freelancers
> "💰 Potential client: '$5K project inquiry from startup'"

### For Travelers
> "✈️ Flight DL-456 delayed 2 hours. New departure: 3:45 PM"

### For Executives
> "🔴 CEO sent: 'Board meeting rescheduled'"

## 🆓 Free Tier Limits

| Service | Free Limit | Paid When |
|---------|-----------|-----------|
| **Groq API** | 500 req/day | After 500 |
| **Telegram** | Unlimited | Never |
| **Gmail IMAP** | Unlimited | Never |
| **LangSmith** | 50K traces/mo | After 50K |
| **Railway** | $5 credit/mo | After $5 |

**Total Cost: $0/month for personal use!**

## 🔍 LangSmith Tracing

To debug why emails were classified a certain way:

```bash
# Enable tracing in .env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your-key

# View traces at: https://smith.langchain.com
```

## 🚀 Deployment

### Railway (Recommended)

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Initialize project
railway init

# 4. Add environment variables
railway variables set GROQ_API_KEY=xxx TELEGRAM_BOT_TOKEN=xxx

# 5. Deploy
railway up

# 6. Add cron job for 7 AM daily
railway cron add "0 7 * * *" "python standalone/scheduler.py"
```

### GitHub Actions (Free Scheduling)

```yaml
# .github/workflows/daily-digest.yml
name: Daily Email Digest
on:
  schedule:
    - cron: '0 7 * * *'  # 7 AM UTC
jobs:
  send-digest:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: pip install -r requirements.txt
      - run: python standalone/bot.py
        env:
          GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
```

## 🛠️ Commands

### Standalone Bot
```bash
# One-time check
python standalone/bot.py

# Run on schedule (7 AM daily)
python standalone/scheduler.py
```

### MCP Server (Local)
```bash
# Start MCP server
python mcp/server.py

# Test tools
curl http://localhost:8000/tools
```

### MCP Server (Remote)
```bash
# Deploy to Railway
railway up

# SSE endpoint: https://your-app.railway.app/sse
```

## 🧪 Testing

```bash
# Run tests
pytest tests/

# Test classification
python tests/test_classifier.py

# Test Telegram
python tests/test_telegram.py
```

## 📝 License

MIT License - Feel free to use for personal or commercial projects!

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 🙏 Acknowledgments

- [Gary Explains - ERIC](https://github.com/garyexplains/examples/tree/master/eric) for IMAP inspiration
- [LangGraph](https://github.com/langchain-ai/langgraph) for workflow orchestration
- [FastMCP](https://github.com/prefecthq/fastmcp) for MCP server framework
- [Groq](https://groq.com/) for fast, free LLM API

## 📞 Support

- Telegram: [@YourBot](https://t.me/YourBot)
- GitHub Issues: [Create an issue](https://github.com/yourusername/email-bridge/issues)
