# Interactive Buttons - Auto Setup

## The Problem

Telegram **requires HTTPS** for webhooks. Your local MCP server runs on `http://localhost`, which Telegram won't accept.

## Solution Options

### Option 1: Use ngrok (Recommended for Testing)

**1. Install ngrok** (one time):
```bash
# Download from https://ngrok.com/download
# Or install with scoop/choco:
scoop install ngrok
```

**2. Start ngrok** (each session):
```bash
ngrok http 8765
```

This gives you an HTTPS URL like: `https://abc123.ngrok.io`

**3. Set webhook** (ask your AI assistant):
```
Use the setup_webhook tool with ngrok_url: https://abc123.ngrok.io
```

Or run manually:
```bash
python webhook_setup.py set https://abc123.ngrok.io
```

### Option 2: Deploy to Cloud (Production)

Deploy to Railway, Render, or similar for a permanent HTTPS URL.

### Option 3: Skip Webhook (Buttons Display Only)

The webhook server **auto-starts** when MCP loads, but without HTTPS:
- ✅ Buttons **display** on urgent alerts
- ❌ Buttons **don't work** when clicked (Telegram can't reach your server)
- ✅ All other MCP tools work normally

## Quick Start

```bash
# Terminal 1: MCP server (auto-starts webhook on port 8765)
# Just use Email Bridge MCP in Claude Desktop - it's automatic!

# Terminal 2: ngrok (for HTTPS tunnel)
ngrok http 8765

# Terminal 3: Set webhook (one time, after getting ngrok URL)
python webhook_setup.py set https://YOUR-NGROK-URL.ngrok.io
```

## New MCP Tools

When using Email Bridge MCP, you now have these tools:

| Tool | Description |
|------|-------------|
| `setup_webhook(ngrok_url)` | Register webhook with Telegram |
| `get_webhook_info()` | Check current webhook status |

## Example Conversation

```
You: "Set up the webhook for interactive buttons"

Assistant: "I'll use the setup_webhook tool. What's your ngrok URL?"

You: "https://abc123.ngrok.io"

Assistant: [calls setup_webhook(ngrok_url="https://abc123.ngrok.io")]

Result: ✅ Webhook set successfully!
```

## Testing

After setup:

1. Send a test urgent alert
2. Click the buttons in Telegram
3. See confirmation messages!

```bash
# Test from Python
python -c "from core.telegram import TelegramSender; import os; tg = TelegramSender(); tg.send_urgent_alert_with_buttons('Test', '123', 'Test Subject')"
```

## Troubleshooting

**Buttons don't work:**
- Check ngrok is running: `ngrok http 8765`
- Check webhook is set: `python webhook_setup.py info`
- Webhook URL must match ngrok URL exactly

**Webhook server not starting:**
- Check MCP server logs for "Webhook server started"
- Port 8765 must be available

**Telegram shows error:**
- HTTPS is required (not HTTP)
- URL must be publicly accessible
