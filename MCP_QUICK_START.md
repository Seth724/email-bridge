# Quick Start: Connect Email Bridge to Claude Desktop

**How to use Email Bridge MCP server with Claude in 5 minutes.**

---

## ⚡ Quick Checklist

- [ ] `.env` file created with all 5 credentials
- [ ] Tested locally: `python standalone/bot.py` (works?)
- [ ] Have Claude Desktop installed
- [ ] Found `claude_desktop_config.json` file
- [ ] Updated config with Email Bridge path
- [ ] Restarted Claude Desktop

---

## 📁 Find Claude's Config File

### Windows:
```
%APPDATA%\Claude\claude_desktop_config.json
```

Or open Explorer and paste into address bar:
```
%APPDATA%\Claude\
```

### Mac:
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

### Linux:
```
~/.config/Claude/claude_desktop_config.json
```

---

## 🔧 Update Config File

**Before (template):**
```json
{
  "mcpServers": {}
}
```

**After (add Email Bridge):**

=== "Windows Path" 

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

=== "Mac Path"

```json
{
  "mcpServers": {
    "email-bridge": {
      "command": "python",
      "args": [
        "/Users/YOUR_USERNAME/Desktop/email-bridge/mcp/server.py"
      ],
      "cwd": "/Users/YOUR_USERNAME/Desktop/email-bridge"
    }
  }
}
```

### Replace These:
- `YOUR_USERNAME` → Your actual username
- Path → Where you cloned email-bridge repo

**How to find your path:**
```bash
# In Terminal/PowerShell, navigate to email-bridge folder and run:
pwd  # Mac/Linux
cd  # Windows (shows current path)
```

---

## 🚀 Restart Claude & Test

1. **Close Claude completely** (from system tray if running)
2. **Reopen Claude Desktop**
3. **Look for "Tools" button** in the toolbar
4. **Should show "Email Bridge"** with ✅ checkmark

### If You See ❌ Error:

1. Check file path in config (typo?)
2. Verify `.env` file exists in email-bridge folder
3. Test MCP manually:
   ```bash
   python mcp/server.py
   ```
4. Check Python version: `python --version` (needs 3.10+)

---

## 💬 Start Using in Claude

### Command 1: Check Your Emails
```
What urgent emails do I have?
```

Claude response:
```
Checking your Gmail...
Found 2 urgent emails:
  🚨 Security Alert from Google
  🚨 Microsoft Account Update
```

### Command 2: Get Summary
```
Summarize my emails for today
```

Claude calls `check_emails()` and gives you:
```
📊 Email Summary
- 2 Urgent (need immediate action)
- 5 Important (review this week)
- 12 Normal
```

### Command 3: Send to Telegram
```
Send "Meeting at 3 PM" to my Telegram
```

Claude calls `send_telegram_message()`:
```
✅ Message sent to Telegram
You'll receive it on your phone instantly
```

### Command 4: Test Connection
```
Test Gmail and Telegram connection
```

Claude response:
```
Testing...
✅ Gmail: Connected (5 unread emails)
✅ Telegram: Connected
✅ Groq AI: Ready
```

### Command 5: Get Urgent-Only Summary
```
What do I need to handle right now?
```

Claude calls `get_urgent_summary()`:
```
🚨 URGENT (3):
• Security alert (Google)
  Action: Check account
  
• Password reset (Microsoft)
  Action: Verify you authorized this
  
• Bank transfer (Chase)
  Action: Confirm transaction
```

---

## 🎯 Cool Use Cases

### Use Case 1: Work Morning Briefing
**Ask Claude:**
```
My morning email briefing - what's important? Anything urgent?
```

**Claude does:**
1. Calls `check_emails()`
2. Filters for URGENT + IMPORTANT
3. Summarizes with priorities
4. Suggests actions

---

### Use Case 2: Auto-Send Alerts
**Ask Claude:**
```
I'm about to go into a meeting. Alert me on Telegram if any urgent emails arrive.
Can you check every 5 minutes and send urgent ones to Telegram?
```

**Claude could:**
1. Start a timer
2. Call `check_emails()` every 5 min
3. Send urgent emails to Telegram via `send_telegram_message()`
4. Keep you informed without interrupting

---

### Use Case 3: Email Analysis
**Ask Claude:**
```
Analyze my emails. Are there any suspicious patterns? Any phishing attempts?
```

**Claude does:**
1. Gets all emails
2. Uses AI reasoning to spot patterns
3. Flags suspicious senders
4. Recommends actions

---

### Use Case 4: Smart Prioritization
**Ask Claude:**
```
Which emails actually need my attention? Ignore promotions and newsletters.
```

**Claude:**
1. Calls `check_emails()`
2. Uses hybrid logic (rules + AI classification)
3. Filters out noise
4. Shows only actionable emails

---

### Use Case 5: Integration with Other Tools
**Ask Claude:**
```
Based on my urgent emails, create a TODO list for today
```

**Claude:**
1. Gets urgent emails with `check_emails()`
2. Extracts action items
3. Creates structured TODO list
4. Shows you organized priorities

---

## ⚙️ Configuration

### Change Email Check Limit
Modify in Claude's request:
```
Check my last 20 emails from the past 3 days
```

The `check_emails()` tool supports:
- `limit` (1-50, default 10)
- `days_back` (1-30, default 1)

---

### Change Quiet Hours
Edit `.env` or `.env` comments for these settings:
```env
# In core/time_urgency.py - modify for your timezone
QUIET_HOURS_START=22  # 10 PM
QUIET_HOURS_END=7     # 7 AM
```

---

### Enable Custom Rules
Edit `config/rules.ini` to add rules that classify emails WITHOUT using Groq AI:

Example:
```ini
[sender-rules]
# Recipients from these senders are URGENT
urgent_sender_1 = boss@company.com
urgent_sender_2 = cto@company.com

[keyword-rules]
# Emails with these keywords are IMPORTANT
important_keyword_1 = meeting
important_keyword_2 = deadline
```

Benefits:
- Faster classification
- Lower costs (skips $0.001 AI call)
- More control

---

## 🔐 Security Notes

### ✅ Safe:
- Credentials in `.env` (gitignored)
- `.env` never pushed to GitHub
- Each user has own credentials
- MCP runs locally (data stays on your machine)

### ⚠️ Be Careful:
- Don't share Claude config with credentials visible
- Don't expose `.env` file
- Rotate passwords if credentials leak
- Only use app-specific passwords (not your main password)

---

## 🐛 Common Issues

### Claude Says "No Tools Available"
```
❌ Could not load Email Bridge tools
```

**Fix:**
1. Close Claude completely
2. Check config file for typos
3. Verify path exists: `ls "C:\path\to\email-bridge"`
4. Reopen Claude

### "GMAIL_ADDRESS not found"
```
Error: Missing GMAIL_ADDRESS environment variable
```

**Fix:**
1. Check `.env` file exists in email-bridge folder
2. Verify it has: `GMAIL_ADDRESS=your-email@gmail.com`
3. Restart Claude

### "Failed to connect to Gmail"
```
Error connecting to IMAP: login failed
```

**Fix:**
1. Verify Gmail App Password (16 chars, NOT main password)
2. Enable 2-Step Verification in Google Account
3. Create new app password
4. Update `.env` and restart Claude

### "Telegram not responding"
```
Error sending message to Telegram
```

**Fix:**
1. Verify bot token is correct
2. Verify chat ID is correct
3. Start a message with bot: `@YourBotName /start`
4. Check bot isn't rate-limited

---

## 📊 What Data Flows Where

```
YOUR COMPUTER
├── Claude Desktop
│   └─ (calls tools)
│
├── Email Bridge MCP Server
│   └─ (runs tools)
│
├── Your Gmail Account (IMAP)
│   └─ (fetches emails)
│
├── Groq API (Cloud)
│   └─ (classifies emails)
│
└── Your Telegram Bot
    └─ (sends messages)

DATA FLOW:
Your Local Machine ←→ Groq Cloud (classification) ←→ Telegram Cloud (notifications)

WHAT'S STORED:
✅ Locally: Email content (in memory, not saved)
✅ Groq: Only for classification (not stored after)
✅ Telegram: Messages you send
✅ GitHub: Code only (no credentials)
```

---

## 📞 Next Steps

1. **Test it works:**
   ```bash
   python standalone/bot.py
   ```

2. **Connect to Claude:**
   - Update config
   - Restart Claude
   - Test in chat

3. **Set up daily digest (optional):**
   - Add GitHub secrets
   - Workflow runs at 7 AM daily

4. **Customize:**
   - Edit `config/rules.ini` for custom rules
   - Adjust quiet hours in `.env`
   - Add more email accounts (requires code changes)

---

## 💡 Tips

- Use Claude to **summarize** emails while you're busy
- Use Claude to **analyze** suspicious emails
- Use Telegram alerts for **urgent emails** while mobile
- Use custom rules to **save money** (skip AI for obvious emails)
- Use MCP to **integrate** emails with other Claude tools

---

**Happy emailing! 📧**

