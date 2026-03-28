"""
Set up Telegram webhook for button callbacks

Run this script to register your webhook URL with Telegram.
Required for interactive button callbacks to work.
"""

import os
import sys
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def set_webhook(webhook_url: str) -> bool:
    """
    Register webhook with Telegram
    
    Args:
        webhook_url: Public URL where Telegram will send updates
        
    Returns:
        True if successful
    """
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN not set in .env file")
        return False
    
    url = f"https://api.telegram.org/bot{bot_token}/setWebhook"
    
    payload = {
        "url": webhook_url,
        "allowed_updates": ["callback_query", "message"],
    }
    
    try:
        print(f"📡 Setting webhook to: {webhook_url}")
        response = requests.post(url, json=payload, timeout=10)
        result = response.json()
        
        if result.get("ok"):
            print(f"✅ Webhook set successfully!")
            print(f"   URL: {webhook_url}")
            print(f"   Allowed updates: callback_query, message")
            return True
        else:
            print(f"❌ Failed to set webhook: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def get_webhook_info() -> dict:
    """Get current webhook information"""
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not bot_token:
        return {"error": "TELEGRAM_BOT_TOKEN not set"}
    
    url = f"https://api.telegram.org/bot{bot_token}/getWebhookInfo"
    
    try:
        response = requests.get(url, timeout=10)
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def delete_webhook() -> bool:
    """Delete registered webhook"""
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN not set")
        return False
    
    url = f"https://api.telegram.org/bot{bot_token}/deleteWebhook"
    
    try:
        response = requests.post(url, timeout=10)
        result = response.json()
        
        if result.get("ok"):
            print("✅ Webhook deleted successfully")
            return True
        else:
            print(f"❌ Failed to delete webhook: {result}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("📧 Email Bridge - Webhook Setup")
        print()
        print("Usage:")
        print("  python webhook_setup.py set <webhook_url>")
        print("  python webhook_setup.py info")
        print("  python webhook_setup.py delete")
        print()
        print("Examples:")
        print("  # For local testing with ngrok")
        print("  python webhook_setup.py set https://abc123.ngrok.io/webhook")
        print()
        print("  # For Railway/Render deployment")
        print("  python webhook_setup.py set https://your-app.railway.app/webhook")
        print()
        print("  # Check current webhook")
        print("  python webhook_setup.py info")
        print()
        print("  # Remove webhook")
        print("  python webhook_setup.py delete")
        return
    
    command = sys.argv[1].lower()
    
    if command == "set":
        if len(sys.argv) < 3:
            print("❌ Please provide webhook URL")
            print("   Usage: python webhook_setup.py set <webhook_url>")
            return
        
        webhook_url = sys.argv[2]
        success = set_webhook(webhook_url)
        
        if success:
            print()
            print("📝 Next steps:")
            print("1. Start the webhook server:")
            print("   python webhook_server.py")
            print()
            print("2. Click buttons on urgent email alerts")
            print("   (Make sure your webhook URL is publicly accessible)")
        
    elif command == "info":
        info = get_webhook_info()
        print("📡 Current Webhook Info:")
        print(info)
        
    elif command == "delete":
        delete_webhook()
        
    else:
        print(f"❌ Unknown command: {command}")
        print("Use 'set', 'info', or 'delete'")


if __name__ == "__main__":
    main()
