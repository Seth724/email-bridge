# Interactive Button Callbacks

This feature enables **interactive buttons** on Telegram urgent email alerts to actually work when clicked.

## Overview

When you receive an urgent email alert, it includes buttons:
- 📧 **Open in Gmail** - Opens email in Gmail (works immediately)
- ✅ **Mark as Read** - Marks email as read (requires webhook)
- 🗑️ **Archive** - Archives the email (requires webhook)
- 📋 **Copy Subject** - Shows subject for copying (requires webhook)

## How It Works

```
User clicks button
       ↓
Telegram sends POST to your webhook URL
       ↓
webhook_server.py receives the callback
       ↓
WebhookHandler processes the action
       ↓
Gmail API performs the action (mark read, archive, etc.)
       ↓
Telegram shows confirmation to user
```

## Setup Instructions

### Step 1: Start the Webhook Server

```bash
# From the email-bridge directory
python webhook_server.py
```

This starts a FastAPI server on `http://localhost:8000`

### Step 2: Expose Your Local Server (for testing)

Telegram needs a **public HTTPS URL** to send webhooks. Use **ngrok** for local testing:

```bash
# Install ngrok (if not installed)
# Download from: https://ngrok.com/

# Start ngrok tunnel
ngrok http 8000
```

This gives you a URL like: `https://abc123.ngrok.io`

### Step 3: Register the Webhook

```bash
# Set webhook URL with Telegram
python webhook_setup.py set https://abc123.ngrok.io/webhook
```

### Step 4: Verify Webhook

```bash
# Check webhook status
python webhook_setup.py info
```

Expected output:
```json
{
  "ok": true,
  "result": {
    "url": "https://abc123.ngrok.io/webhook",
    "has_custom_certificate": false,
    "pending_update_count": 0,
    ...
  }
}
```

## Deployment Options

### Option 1: Local Testing (ngrok)

```bash
# Terminal 1: Start webhook server
python webhook_server.py

# Terminal 2: Start ngrok
ngrok http 8000

# Terminal 3: Set webhook (use the ngrok URL)
python webhook_setup.py set https://YOUR-NGROK-ID.ngrok.io/webhook
```

**Note:** ngrok URL changes each time you restart. Re-run `webhook_setup.py set` with the new URL.

### Option 2: Railway/Render Deployment

When deployed to Railway, Render, or similar:

```bash
# Your app will have a permanent URL
# e.g., https://email-bridge.railway.app

# Set webhook once
python webhook_setup.py set https://email-bridge.railway.app/webhook
```

### Option 3: GitHub Actions (Scheduled)

For the standalone bot/scheduler, webhooks are **not needed**. Buttons will display but won't work.

Webhooks are only for **real-time button interactions**.

## Available Commands

The webhook server also handles bot commands:

- `/start` - Welcome message
- `/help` - Show help
- `/status` - Check connection
- `/settings` - View settings

## Troubleshooting

### Buttons don't respond when clicked

1. **Check webhook is set:**
   ```bash
   python webhook_setup.py info
   ```

2. **Check server is running:**
   ```bash
   curl http://localhost:8000/health
   ```

3. **Check ngrok is running:**
   - Verify ngrok tunnel is active
   - URL hasn't changed

4. **Check logs:**
   - Webhook server logs should show incoming requests
   - Look for errors in the callback processing

### Webhook returns error 404

- Ensure the webhook URL ends with `/webhook`
- Example: `https://abc123.ngrok.io/webhook`

### Actions don't affect Gmail

- Verify `GMAIL_ADDRESS` and `GMAIL_APP_PASSWORD` in `.env`
- Check Gmail IMAP access is enabled
- Review webhook server logs for errors

## Security Notes

- Webhook URL should be HTTPS (Telegram requires this)
- Consider adding webhook secret validation for production
- Don't commit `.env` file with credentials

## Files Added

| File | Purpose |
|------|---------|
| `core/webhook_handler.py` | Processes callback actions |
| `webhook_server.py` | FastAPI server for webhooks |
| `webhook_setup.py` | Webhook registration utility |
| `WEBHOOK_README.md` | This documentation |

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/webhook` | POST | Telegram webhook receiver |
| `/health` | GET | Health check |
| `/` | GET | Service info |

## Next Steps

After setup:
1. Trigger an urgent email (or use test function)
2. Click buttons on the Telegram alert
3. See confirmation messages
4. Verify actions in Gmail

Enjoy your interactive email notifications! 🎉
