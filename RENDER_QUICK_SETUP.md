# ✅ Correct Render Deployment Setup

## The Issue

❌ **Wrong:** `startCommand: python webhook_server.py`
- Only runs webhook server
- MCP server doesn't run
- Claude Desktop can't connect

✅ **Correct:** `startCommand: python combined_server.py`
- Runs BOTH MCP server AND webhook server
- Claude Desktop can connect
- Telegram buttons work

---

## What `combined_server.py` Does

```
combined_server.py
├── Main Thread: FastMCP Server
│   ├── Endpoint: /mcp (or /sse)
│   └── Tools: check_emails, send_voice_summary, etc.
│
└── Background Thread: Webhook Server
    ├── Endpoint: /webhook
    └── Handles: Button callbacks from Telegram
```

**Both run on same port (8000), different paths!**

---

## Render Configuration

### render.yaml (Already Configured)

```yaml
services:
  - type: web
    name: email-bridge
    env: python
    startCommand: python combined_server.py  # ✅ Correct!
    buildCommand: pip install -r requirements.txt && pip install -r requirements-audio.txt
    healthCheckPath: /health
```

### Environment Variables

```
GMAIL_ADDRESS = your.email@gmail.com
GMAIL_APP_PASSWORD = xxxxxxxx
TELEGRAM_BOT_TOKEN = 123456:ABC-DEF...
TELEGRAM_CHAT_ID = 123456789
GROQ_API_KEY = gsk_xxxxx
DEPLOYMENT_MODE = remote
MCP_TRANSPORT = streamable-http
PUBLIC_URL = https://email-bridge.onrender.com
PORT = 8000
```

---

## Endpoints After Deploy

| URL | Purpose |
|-----|---------|
| `https://email-bridge.onrender.com/mcp` | MCP server (Claude Desktop) |
| `https://email-bridge.onrender.com/sse` | MCP SSE (alternative) |
| `https://email-bridge.onrender.com/webhook` | Telegram callbacks |
| `https://email-bridge.onrender.com/health` | Health check |

---

## Claude Desktop Config

```json
{
  "mcpServers": {
    "email-bridge": {
      "url": "https://email-bridge.onrender.com/mcp"
    }
  }
}
```

---

## Test After Deploy

```bash
# 1. Check health
curl https://email-bridge.onrender.com/health
# Returns: {"status": "healthy", "service": "email-bridge-webhook"}

# 2. Check MCP endpoint
curl https://email-bridge.onrender.com/mcp
# Returns: {"service": "Email Bridge MCP", "status": "running", ...}

# 3. Check webhook
python webhook_setup.py info
# Returns: {"url": "https://email-bridge.onrender.com/webhook", ...}

# 4. Test buttons
python -c "from core.telegram import TelegramSender; import os; tg = TelegramSender(); tg.send_urgent_alert_with_buttons('Test', '123', 'Test')"
```

---

## Files You Need

| File | Purpose |
|------|---------|
| `combined_server.py` | ✅ Runs both servers |
| `webhook_server.py` | Webhook server (used by combined) |
| `mcp/server.py` | MCP server (used by combined) |
| `render.yaml` | Render config (already set to combined_server.py) |

---

## Quick Deploy Checklist

- [ ] Push code to GitHub
- [ ] Create Render web service
- [ ] Set `startCommand: python combined_server.py`
- [ ] Add all environment variables
- [ ] Deploy
- [ ] Wait for health check to pass
- [ ] Update Claude Desktop config
- [ ] Test in Claude Desktop: "Check my emails"
- [ ] Test buttons in Telegram

---

## Summary

**Use `combined_server.py`** - it's designed specifically for Render/Railway deployment where you need both:
1. MCP server (for Claude Desktop)
2. Webhook server (for Telegram buttons)

Both run together on one port! 🎉
