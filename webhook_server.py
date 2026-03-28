"""
Telegram Webhook Server

FastAPI server to handle Telegram webhook callbacks from inline buttons.
Receives updates from Telegram Bot API and processes callback queries.
"""

import os
import logging
from typing import Optional
from dotenv import load_dotenv

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import uvicorn

from core.webhook_handler import WebhookHandler

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Email Bridge Webhook Server")

# Initialize webhook handler
handler = WebhookHandler()


@app.on_event("startup")
async def startup_event():
    """Set up webhook on startup if deployed remotely"""
    deployment_mode = os.getenv("DEPLOYMENT_MODE", "").lower()
    public_url = os.getenv("PUBLIC_URL")  # e.g., https://app.railway.app
    
    if deployment_mode == "remote" and public_url:
        webhook_url = f"{public_url}/webhook"
        await set_webhook(webhook_url)
        logger.info(f"Auto-registered webhook: {webhook_url}")
    else:
        logger.info("Running locally - webhook not auto-registered (use setup_webhook tool)")


@app.get("/mcp")
async def mcp_info():
    """MCP server info endpoint"""
    return {
        "service": "Email Bridge MCP",
        "status": "running",
        "endpoints": {
            "mcp": "/mcp (streamable-http)",
            "sse": "/sse",
            "webhook": "/webhook (POST)",
            "health": "/health",
        }
    }


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    handler.close()


async def set_webhook(webhook_url: str):
    """Register webhook with Telegram"""
    import requests
    
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    url = f"https://api.telegram.org/bot{bot_token}/setWebhook"
    
    payload = {
        "url": webhook_url,
        "allowed_updates": ["callback_query"],
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        result = response.json()
        
        if result.get("ok"):
            logger.info(f"Webhook set successfully: {webhook_url}")
        else:
            logger.error(f"Failed to set webhook: {result}")
    except Exception as e:
        logger.error(f"Error setting webhook: {e}")


@app.post("/webhook")
async def handle_webhook(request: Request) -> JSONResponse:
    """
    Handle incoming Telegram webhook updates
    
    Telegram sends POST requests to this endpoint when:
    - User clicks an inline button
    - User sends a command to the bot
    """
    try:
        update = await request.json()
        logger.debug(f"Received update: {update}")
        
        # Handle callback queries (button clicks)
        if "callback_query" in update:
            callback_query = update["callback_query"]
            callback_id = callback_query.get("id")
            callback_data = callback_query.get("data", "")
            message = callback_query.get("message", {})
            message_id = message.get("message_id")
            chat_id = message.get("chat", {}).get("id")
            
            logger.info(f"Callback query: id={callback_id}, data={callback_data}")
            
            # Process the callback
            result = handler.handle_callback(
                callback_data=callback_data,
                message_id=message_id,
                chat_id=str(chat_id),
            )
            
            # Send answer to callback query
            await answer_callback(
                callback_id=callback_id,
                text=result["answer_text"],
                show_alert=result["show_alert"],
            )
            
            return JSONResponse({"status": "ok"})
        
        # Handle regular messages (commands)
        if "message" in update:
            message = update["message"]
            chat_id = message.get("chat", {}).get("id")
            text = message.get("text", "")
            
            if text.startswith("/"):
                await handle_command(chat_id, text, message)
            
            return JSONResponse({"status": "ok"})
        
        return JSONResponse({"status": "ignored"})
        
    except Exception as e:
        logger.error(f"Error handling webhook: {e}")
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)


async def answer_callback(
    callback_id: str,
    text: str,
    show_alert: bool = False,
):
    """Send answer to callback query"""
    import requests
    
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    url = f"https://api.telegram.org/bot{bot_token}/answerCallbackQuery"
    
    payload = {
        "callback_query_id": callback_id,
        "text": text,
        "show_alert": show_alert,
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        result = response.json()
        
        if not result.get("ok"):
            logger.error(f"Failed to answer callback: {result}")
    except Exception as e:
        logger.error(f"Error answering callback: {e}")


async def handle_command(chat_id: int, command: str, message: dict):
    """Handle bot commands"""
    import requests
    
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    # Parse command
    cmd = command.split()[0].lower()
    
    if cmd == "/start":
        text = """👋 Welcome to Email Bridge!

I'll notify you about important emails.

Commands:
/help - Show help
/status - Check connection
/settings - View settings"""
    elif cmd == "/help":
        text = """📧 Email Bridge Help

I monitor your Gmail and send notifications for urgent/important emails.

Buttons on urgent alerts:
• 📧 Open in Gmail - Open the email
• ✅ Mark as Read - Mark email as read
• 🗑️ Archive - Archive the email
• 📋 Copy Subject - Copy subject text

Commands:
/start - Start the bot
/status - Check connection
/settings - View settings"""
    elif cmd == "/status":
        text = "✅ Email Bridge is running!"
    elif cmd == "/settings":
        text = """⚙️ Settings

Notifications are enabled.
Check your .env file for configuration."""
    else:
        text = f"❓ Unknown command: {cmd}\nUse /help for available commands."
    
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
    }
    
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        logger.error(f"Error sending command response: {e}")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "email-bridge-webhook"}


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Email Bridge Webhook Server",
        "status": "running",
        "endpoints": {
            "webhook": "/webhook (POST)",
            "health": "/health (GET)",
        }
    }


def main():
    """Run the webhook server"""
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    
    logger.info(f"Starting webhook server on {host}:{port}")
    
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
