# Email Bridge with Qwen CLI - Complete Setup Guide

Deploy Email Bridge as an MCP server and integrate with Qwen CLI for intelligent email management through Alibaba's Qwen AI.

---

## 📋 Overview

**Email Bridge + Qwen CLI:**
- ✅ Deploy Email Bridge as MCP server
- ✅ Connect Qwen CLI to Email Bridge
- ✅ Ask Qwen to check/manage your emails
- ✅ Get AI responses in Qwen's interface
- ✅ Same features as Claude Desktop integration

**Architecture:**
```
Qwen CLI
   ↓ (MCP Protocol)
Email Bridge MCP Server
   ├─ Gmail (fetch emails)
   ├─ Groq AI (classify)
   └─ Telegram (send alerts)
```

---

## 📦 Prerequisites

### 1. Prerequisites You Already Have
- ✅ Email Bridge installed (`d:\MetaruneLabs\mcp-server\email-bridge`)
- ✅ `.env` file with credentials
- ✅ Python 3.10+

### 2. Install Qwen CLI

**Windows (PowerShell):**
```powershell
# Install via pip
pip install qwen-cli

# Verify installation
qwen --version
```

**Mac/Linux:**
```bash
pip install qwen-cli
qwen --version
```

### 3. Get Qwen API Key

1. Go to [Qwen Console](https://dashscope.console.aliyun.com/)
2. Sign up or login
3. Create API key under "API Keys"
4. Copy the key (starts with `sk-`)

---

## 🚀 Setup Steps

### Step 1: Configure Qwen CLI

**Create Qwen config file:**

**Windows:**
```powershell
# Config location: %USERPROFILE%\.qwen\config.json
mkdir -Path "$env:USERPROFILE\.qwen" -Force

# Create config.json with text editor
notepad "$env:USERPROFILE\.qwen\config.json"
```

**Mac/Linux:**
```bash
mkdir -p ~/.qwen
nano ~/.qwen/config.json
```

**Add this content:**
```json
{
  "api_key": "sk_your_qwen_api_key_here",
  "model": "qwen-max",
  "temperature": 0.7,
  "max_tokens": 2048,
  "timeout": 30
}
```

### Step 2: Register Email Bridge as MCP Server

Add MCP server configuration to Qwen:

**Windows:**
```powershell
# Create Qwen MCP config
notepad "$env:USERPROFILE\.qwen\mcp_servers.json"
```

**Add this:**
```json
{
  "mcpServers": {
    "email-bridge": {
      "command": "python",
      "args": [
        "D:\\MetaruneLabs\\mcp-server\\email-bridge\\mcp\\server.py"
      ],
      "cwd": "D:\\MetaruneLabs\\mcp-server\\email-bridge",
      "env": {
        "PYTHONPATH": "D:\\MetaruneLabs\\mcp-server\\email-bridge"
      }
    }
  }
}
```

**Mac/Linux:**
```bash
nano ~/.qwen/mcp_servers.json
```

```json
{
  "mcpServers": {
    "email-bridge": {
      "command": "python3",
      "args": [
        "/path/to/email-bridge/mcp/server.py"
      ],
      "cwd": "/path/to/email-bridge",
      "env": {
        "PYTHONPATH": "/path/to/email-bridge"
      }
    }
  }
}
```

### Step 3: Test MCP Connection

**Via Qwen CLI:**
```bash
qwen --mcp email-bridge test
```

Expected output:
```
✅ Email Bridge MCP server connected
✅ Tools available:
   - check_emails
   - get_urgent_summary
   - send_telegram_message
   - test_connection
   - classify_email_sample
```

### Step 4: Start Using

**Start Qwen CLI:**
```bash
qwen --mcp email-bridge
```

**Interactive mode:**
```
Qwen> Check my urgent emails
```

---

## 💬 Usage Examples with Qwen CLI

### Example 1: Check Emails

```bash
$ qwen --mcp email-bridge
Qwen> What urgent emails do I have?

Qwen Assistant:
I'll check your urgent emails using the Email Bridge tool.

[Calling Email Bridge tool: get_urgent_summary()]

🚨 URGENT EMAILS (3):

1. **Security Alert** - Google
   Summary: App password created for your account
   Action: Verify account activity

2. **Microsoft Account Alert**
   Summary: Security info was added
   Action: Review recent login activity

3. **Bank Transaction Alert**
   Summary: Charge of $500 from AWS
   Action: Approve or dispute transaction
```

### Example 2: Full Summary

```bash
Qwen> Summarize all my emails. What needs my attention?

Qwen Assistant:
[Calling: check_emails(limit=20, days_back=1)]

📊 Email Summary:

🚨 URGENT (3): Security alerts and bank transaction
📌 IMPORTANT (5): Meetings, invoices, notifications
📄 NORMAL (12): Promotions, newsletters

Key Actions:
1. Verify AWS charge immediately
2. Check security alerts aren't compromised accounts
3. Accept 2 meeting invites by EOD
4. Review invoice due next week

💡 Analysis: You have 3 urgent items that need immediate attention.
All are security/financial related. Recommend:
- Reset passwords on Google/Microsoft
- Verify AWS charge
- Enable 2FA if not already active
```

### Example 3: Send to Telegram

```bash
Qwen> Send a message to my Telegram: "Meeting at 3 PM today"

Qwen Assistant:
I'll send that message to your Telegram.

[Calling: send_telegram_message(message: "Meeting at 3 PM today")]

✅ Message sent successfully to your Telegram chat!
You'll receive it instantly on your phone.
```

### Example 4: Test Connection

```bash
Qwen> Is everything connected? Test Gmail, Telegram, and Groq AI.

Qwen Assistant:
[Calling: test_connection()]

✅ Connection Status Report:

📧 Gmail: Connected
   Account: amanethmeis@gmail.com
   Unread: 5 emails
   
💬 Telegram: Connected
   Bot: My Email Assistant
   Ready to send messages
   
🤖 Groq AI: Ready
   Model: Llama 3.3 70B
   Cost: $0.001/email

All systems operational!
```

---

## 🔧 Advanced Configuration

### Set Default Model

**In `~/.qwen/config.json`:**
```json
{
  "model": "qwen-max",
  "model_options": {
    "temperature": 0.7,
    "top_p": 0.9,
    "max_tokens": 2048
  }
}
```

### Multiple MCP Servers

If you want to connect other tools besides Email Bridge:

```json
{
  "mcpServers": {
    "email-bridge": {
      "command": "python",
      "args": ["...path to email-bridge..."]
    },
    "other-tool": {
      "command": "python",
      "args": ["...path to other tool..."]
    }
  }
}
```

Then use in Qwen:
```bash
qwen --mcp email-bridge --mcp other-tool
```

### Change Polling Interval

For monitoring urgent emails, modify polling:

```json
{
  "mcp_polling_interval": 300,
  "mcp_timeout": 30
}
```

Values in seconds (300 = 5 minutes)

---

## 📋 Configuration Files Reference

### File Locations

| OS | Location |
|---|---|
| Windows | `%USERPROFILE%\.qwen\` |
| Mac | `~/.qwen/` |
| Linux | `~/.qwen/` |

### Essential Files

**config.json** - Qwen CLI settings
```json
{
  "api_key": "sk_...",
  "model": "qwen-max",
  "temperature": 0.7
}
```

**mcp_servers.json** - MCP server definitions
```json
{
  "mcpServers": {
    "email-bridge": {...}
  }
}
```

**mcp_config.json** (optional) - MCP-specific settings
```json
{
  "timeout": 30,
  "retry_attempts": 3,
  "retry_delay": 1000
}
```

---

## 🚀 Deployment Options

### Option 1: Local Machine (Recommended)
```bash
# Start Qwen CLI with Email Bridge
qwen --mcp email-bridge

# Then use interactively
Qwen> Check my emails
```

**Pros:** Simple, instant, secure
**Cons:** Only works when computer is on

### Option 2: Remote Server (GitHub Actions)

Use GitHub Actions to trigger email checks:

```yaml
# .github/workflows/email-check.yml
name: Email Check
on:
  schedule:
    - cron: '30 1 * * *'  # 7 AM Sri Lanka time

jobs:
  check-emails:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Check emails and send to Telegram
        run: python standalone/bot.py
        env:
          GMAIL_ADDRESS: ${{ secrets.GMAIL_ADDRESS }}
          GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
```

Then in Qwen, manually call checks via MCP.

### Option 3: Docker Container

Create Docker image for Email Bridge MCP:

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
CMD ["python", "mcp/server.py"]
```

**Build & Run:**
```bash
docker build -t email-bridge-mcp .
docker run -e GMAIL_ADDRESS=... -e GROQ_API_KEY=... email-bridge-mcp
```

---

## ⚙️ Troubleshooting

### Issue 1: Qwen CLI Won't Connect to Email Bridge

**Error:**
```
Error: Failed to connect to MCP server 'email-bridge'
```

**Solutions:**
1. Check path in `mcp_servers.json` is correct
2. Test MCP server directly:
   ```bash
   python mcp/server.py
   ```
3. Verify `.env` file exists with all credentials
4. Check Python version: `python --version` (needs 3.10+)

### Issue 2: "Tools unavailable" in Qwen

**Error:**
```
Qwen> Check emails
Response: No tools available from email-bridge
```

**Solutions:**
1. Verify MCP server is running
2. Check `mcp_servers.json` syntax (valid JSON?)
3. Restart Qwen CLI: `qwen --reset`
4. Check credentials in `.env`:
   ```bash
   python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('GMAIL_ADDRESS'))"
   ```

### Issue 3: Gmail Connection Fails

```
Error: Failed to connect to Gmail
```

**Solutions:**
1. Verify Gmail App Password (16 chars)
2. Check Gmail address is correct
3. Test separately:
   ```bash
   python -c "from core.gmail import GmailFetcher; GmailFetcher(...).connect()"
   ```

### Issue 4: Permission Denied (Mac/Linux)

```
bash: qwen: command not found
```

**Solutions:**
```bash
# Install correctly
pip3 install qwen-cli --user

# Add to PATH
export PATH="$PATH:$HOME/.local/bin"
```

---

## 📊 Comparing Interfaces

### Qwen CLI vs Claude Desktop

| Feature | Qwen CLI | Claude Desktop |
|---|---|---|
| **How to use** | Terminal commands | GUI chat interface |
| **Setup** | `config.json` + JSON | GUI + JSON |
| **Performance** | Fast, minimal overhead | Slower, more features |
| **Multimodal** | Text only | Images, files, etc. |
| **Best for** | Developers, automation | General users |
| **Cost** | Qwen API pricing | Free (Claude Plus) |

### When to Use Each

**Qwen CLI (Best for):**
- Server-side automation
- Headless deployments
- Scripting & batch jobs
- Terminal workflows
- Integration with other CLI tools

**Claude Desktop (Best for):**
- Interactive chat experience
- Rich formatting
- Image uploads
- Longer context
- Desktop use

### Can Use Both!
```bash
# Qwen CLI for automation
qwen --mcp email-bridge << EOF
Check urgent emails
EOF

# AND use Claude Desktop for interactive analysis
# Both share the same Email Bridge MCP server
```

---

## 🔒 Security Best Practices

### Keep Credentials Safe

**✅ DO:**
- Store API keys in `.env` or environment variables
- Use app-specific passwords (not main password)
- Restrict file permissions: `chmod 600 ~/.qwen/config.json`
- Rotate keys if exposed

**❌ DON'T:**
- Hardcode credentials in config files
- Commit credentials to GitHub
- Share config files with sensitive data
- Use main Gmail password

### Environment Variable Setup

**Windows (PowerShell):**
```powershell
# Temporary
$env:GMAIL_ADDRESS = "your-email@gmail.com"
$env:GROQ_API_KEY = "sk_..."

# Or use .env file (recommended)
# Create .env in email-bridge folder
```

**Mac/Linux:**
```bash
# In ~/.bashrc or ~/.zshrc
export GMAIL_ADDRESS="your-email@gmail.com"
export GROQ_API_KEY="sk_..."
```

---

## 📈 Scaling & Monitoring

### Monitor MCP Server

```bash
# Check if server is running
ps aux | grep "mcp/server.py"

# View logs (if enabled)
tail -f logs/email_bridge.log

# Test periodically
qwen --mcp email-bridge test
```

### Performance Optimization

**For high-volume usage:**

1. **Enable caching** (optional enhancement)
   - Cache email classifications for 1 hour
   - Reduces API calls to Groq

2. **Use rules engine**
   - Configure `config/rules.ini`
   - Match common emails without AI
   - Save ~$0.001 per matched email

3. **Batch operations**
   - Instead of checking emails 10x/day
   - Check once at 7 AM, once at 5 PM
   - Reduces unnecessary API calls

---

## 🎯 Workflow Examples

### Workflow 1: Morning Briefing (Automated)

```bash
#!/bin/bash
# save as morning-briefing.sh

qwen --mcp email-bridge << EOF
Good morning! What do I need to handle today?
Summarize urgent emails, important items, and recommended actions.
EOF
```

**Run on schedule:**
```bash
# Add to crontab (Mac/Linux)
crontab -e
# Add: 0 7 * * * /path/to/morning-briefing.sh
```

### Workflow 2: Email Monitoring (Loop)

```bash
#!/bin/bash
# Monitor for urgent emails every 5 minutes

while true; do
  qwen --mcp email-bridge << EOF
Check for urgent emails. If found, list them.
EOF
  sleep 300  # 5 minutes
done
```

### Workflow 3: Automated Response

```bash
#!/bin/bash
# Check emails and send alert to Telegram if urgent

qwen --mcp email-bridge << EOF
Check urgent emails. For each one:
1. Summarize in one line
2. Send to Telegram using send_telegram_message tool
EOF
```

---

## 🔄 Integration with Other Tools

### Combine with Other MCP Servers

```json
{
  "mcpServers": {
    "email-bridge": {...},
    "web-search": {
      "command": "python",
      "args": ["path/to/web-search-mcp"]
    },
    "calendar": {
      "command": "python",
      "args": ["path/to/calendar-mcp"]
    }
  }
}
```

### Use in Scripts

```python
# Python script using Email Bridge via Qwen

import subprocess
import json

def check_emails_via_qwen():
    result = subprocess.run(
        ["qwen", "--mcp", "email-bridge"],
        input="Check my urgent emails",
        capture_output=True,
        text=True
    )
    return result.stdout
```

---

## 📚 Additional Resources

- **Qwen Documentation:** https://dashscope.console.aliyun.com/docs
- **MCP Protocol Spec:** https://modelcontextprotocol.io
- **Email Bridge GitHub:** https://github.com/Seth724/email-bridge

---

## ✅ Checklist

- [ ] Install Qwen CLI: `pip install qwen-cli`
- [ ] Get Qwen API key from console.aliyun.com
- [ ] Create `~/.qwen/config.json` with API key
- [ ] Create `~/.qwen/mcp_servers.json` with Email Bridge path
- [ ] Verify `.env` has all 5 credentials
- [ ] Test MCP connection: `qwen --mcp email-bridge test`
- [ ] Start Qwen CLI: `qwen --mcp email-bridge`
- [ ] Test first command: "Check my urgent emails"
- [ ] Set up automation (optional)

---

**Ready to use Email Bridge with Qwen CLI!** 🚀

