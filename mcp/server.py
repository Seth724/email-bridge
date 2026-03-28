"""
FastMCP Server for Email Bridge

Provides email tools to AI assistants via Model Context Protocol.
Supports both local (stdio) and remote (SSE) deployment.
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Avoid shadowing the third-party `mcp` package with this local `mcp` folder
# when deployment platforms import this file as a module from project root.
_SERVER_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_SERVER_DIR)
_removed_entries = []
for _entry in list(sys.path):
    if _entry in ("", ".", _PROJECT_ROOT):
        sys.path.remove(_entry)
        _removed_entries.append(_entry)

from fastmcp import FastMCP

for _entry in reversed(_removed_entries):
    sys.path.insert(0, _entry)


logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.gmail import GmailFetcher
from core.classifier import EmailClassifier
from core.telegram import TelegramSender
from core.audio import send_voice_summary as send_voice_summary_func
from workflows.triage_graph import EmailTriageWorkflow

# Auto-start webhook server in background for interactive button callbacks
_webhook_thread = None


def _start_webhook_background():
    """Start webhook server in background thread"""
    import threading

    def run_server():
        try:
            # Lazy import to avoid dependency issues
            import uvicorn
            from webhook_server import app

            uvicorn.run(app, host="127.0.0.1", port=8765, log_level="warning")
        except ImportError as e:
            logger.debug(f"Webhook dependencies not available: {e}")
        except Exception as e:
            logger.debug(f"Webhook server stopped: {e}")

    _webhook_thread = threading.Thread(target=run_server, daemon=True)
    _webhook_thread.start()
    logger.info("Webhook server started on http://127.0.0.1:8765")


# Start webhook server automatically when MCP server loads
_start_webhook_background()

# Initialize FastMCP server
mcp = FastMCP(
    "Email Bridge",
    instructions="""
    Email Bridge MCP Server - Intelligent email triage and notifications.

    Tools available:
    - check_emails: Fetch and classify unread emails
    - get_urgent_summary: Get summary of urgent emails only
    - send_telegram_message: Send a text message to Telegram
    - send_voice_summary: Send a voice (audio) summary to Telegram
    - test_connection: Test Gmail and Telegram connections
    - classify_email_sample: Classify a sample email (for testing)
    - setup_webhook: Set up Telegram webhook for interactive buttons
    - get_webhook_info: Get current webhook status

    The webhook server auto-starts in the background. Use setup_webhook() to enable interactive button callbacks.
    """,
)


@mcp.tool()
def check_emails(limit: int = 10, days_back: int = 1) -> dict:
    """
    Check unread emails and classify them by priority.
    
    Args:
        limit: Maximum number of emails to fetch (default 10)
        days_back: Only fetch emails from last N days (default 1)
    
    Returns:
        Dictionary with classified emails and summary
    """
    try:
        # Initialize components
        gmail = GmailFetcher(
            email_address=os.getenv("GMAIL_ADDRESS"),
            app_password=os.getenv("GMAIL_APP_PASSWORD"),
        )

        classifier = EmailClassifier(
            api_key=os.getenv("GROQ_API_KEY"),
            model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
        )

        # Fetch emails
        emails = gmail.fetch_unread_emails(limit=limit, days_back=days_back)

        if not emails:
            return {"status": "success", "message": "No unread emails found", "emails": []}

        # Process through workflow
        workflow = EmailTriageWorkflow(classifier)
        result = workflow.process_emails(emails)

        # Disconnect Gmail
        gmail.disconnect()

        return {
            "status": "success",
            "total_emails": len(emails),
            "urgent_count": len(result["urgent_emails"]),
            "important_count": len(result["important_emails"]),
            "classified_emails": result["classified_emails"],
            "summary": result["summary"],
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp.tool()
def get_urgent_summary() -> str:
    """
    Get a summary of only URGENT emails.
    
    Returns:
        Formatted summary string of urgent emails
    """
    try:
        gmail = GmailFetcher(
            email_address=os.getenv("GMAIL_ADDRESS"),
            app_password=os.getenv("GMAIL_APP_PASSWORD"),
        )

        classifier = EmailClassifier(
            api_key=os.getenv("GROQ_API_KEY"),
            model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
        )

        emails = gmail.fetch_unread_emails(limit=20, days_back=1)
        workflow = EmailTriageWorkflow(classifier)
        result = workflow.process_emails(emails)

        gmail.disconnect()

        # Return only urgent summary
        if result["urgent_emails"]:
            summary = "🚨 **URGENT EMAILS**\n\n"
            for email in result["urgent_emails"]:
                summary += f"• {email['email_subject']} (from {email['email_sender']})\n"
                summary += f"  _{email['summary']}_\n"
                summary += f"  **Action**: {email.get('action_needed', 'Review')}\n\n"
            return summary
        else:
            return "✅ No urgent emails. Inbox is clear!"

    except Exception as e:
        return f"❌ Error: {str(e)}"


@mcp.tool()
def send_telegram_message(message: str, urgent: bool = False) -> bool:
    """
    Send a message to Telegram.

    Args:
        message: Message text to send
        urgent: If True, send with sound notification

    Returns:
        True if successful, False otherwise
    """
    try:
        telegram = TelegramSender(
            bot_token=os.getenv("TELEGRAM_BOT_TOKEN"),
            chat_id=os.getenv("TELEGRAM_CHAT_ID"),
        )

        if urgent:
            return telegram.send_message(
                f"🚨 **Alert**\n\n{message}",
                parse_mode="Markdown",
                disable_notification=False,
            )
        else:
            return telegram.send_message(
                message, parse_mode="Markdown", disable_notification=True
            )

    except Exception as e:
        print(f"Error sending Telegram message: {e}")
        return False


@mcp.tool()
def send_voice_summary(summary_text: str) -> bool:
    """
    Send a voice (audio) summary to Telegram.

    Converts text to speech and sends as a voice message.

    Args:
        summary_text: Text to convert to voice message

    Returns:
        True if successful, False otherwise
    """
    try:
        return send_voice_summary_func(summary_text)
    except Exception as e:
        print(f"Error sending voice summary: {e}")
        return False


@mcp.tool()
def test_connection() -> dict:
    """
    Test connections to Gmail and Telegram.
    
    Returns:
        Dictionary with test results
    """
    results = {"gmail": False, "telegram": False, "errors": []}

    # Test Gmail
    try:
        gmail = GmailFetcher(
            email_address=os.getenv("GMAIL_ADDRESS"),
            app_password=os.getenv("GMAIL_APP_PASSWORD"),
        )

        if gmail.connect():
            results["gmail"] = True
            count = gmail.get_email_count(unread_only=True)
            results["unread_count"] = count
            gmail.disconnect()
        else:
            results["errors"].append("Failed to connect to Gmail")

    except Exception as e:
        results["errors"].append(f"Gmail error: {str(e)}")

    # Test Telegram
    try:
        telegram = TelegramSender(
            bot_token=os.getenv("TELEGRAM_BOT_TOKEN"),
            chat_id=os.getenv("TELEGRAM_CHAT_ID"),
        )

        bot_info = telegram.get_me()
        if bot_info:
            results["telegram"] = True
            results["bot_username"] = bot_info.get("username")
        else:
            results["errors"].append("Failed to connect to Telegram")

    except Exception as e:
        results["errors"].append(f"Telegram error: {str(e)}")

    # Overall status
    results["status"] = "success" if all([results["gmail"], results["telegram"]]) else "error"

    return results


@mcp.tool()
def classify_email_sample(subject: str, sender: str, body: str) -> dict:
    """
    Classify a sample email (for testing).

    Args:
        subject: Email subject
        sender: Email sender
        body: Email body text

    Returns:
        Classification result
    """
    try:
        classifier = EmailClassifier(
            api_key=os.getenv("GROQ_API_KEY"),
            model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
        )

        email_data = {"subject": subject, "sender": sender, "body": body}
        result = classifier.classify_email(email_data)

        return result

    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp.tool()
def setup_webhook(ngrok_url: str = None) -> dict:
    """
    Set up Telegram webhook for interactive button callbacks.

    Args:
        ngrok_url: Optional ngrok URL (e.g., "https://abc123.ngrok.io").
                   If not provided, uses localhost for local testing.

    Returns:
        Dictionary with setup status
    """
    import requests

    try:
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not bot_token:
            return {"status": "error", "message": "TELEGRAM_BOT_TOKEN not set"}

        # Determine webhook URL
        if ngrok_url:
            webhook_url = f"{ngrok_url}/webhook"
        else:
            # Use a public tunnel service or localhost
            webhook_url = "http://127.0.0.1:8765/webhook"

        # Register webhook with Telegram
        url = f"https://api.telegram.org/bot{bot_token}/setWebhook"
        payload = {
            "url": webhook_url,
            "allowed_updates": ["callback_query", "message"],
        }

        response = requests.post(url, json=payload, timeout=10)
        result = response.json()

        if result.get("ok"):
            return {
                "status": "success",
                "message": f"Webhook set to {webhook_url}",
                "webhook_url": webhook_url,
                "note": "Interactive buttons will now work when you click them!",
            }
        else:
            return {
                "status": "error",
                "message": f"Failed to set webhook: {result}",
            }

    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp.tool()
def get_webhook_info() -> dict:
    """
    Get current Telegram webhook status.

    Returns:
        Dictionary with webhook information
    """
    import requests

    try:
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not bot_token:
            return {"status": "error", "message": "TELEGRAM_BOT_TOKEN not set"}

        url = f"https://api.telegram.org/bot{bot_token}/getWebhookInfo"
        response = requests.get(url, timeout=10)
        result = response.json()

        return {
            "status": "success" if result.get("ok") else "error",
            "webhook_info": result.get("result", {}),
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}


def main() -> None:
    """Run Email Bridge MCP server in local (stdio) or remote (SSE) mode."""
    import sys

    deployment_mode = os.getenv("DEPLOYMENT_MODE", "").strip().lower()
    run_remote = deployment_mode == "remote" or (
        len(sys.argv) > 1 and sys.argv[1] == "--remote"
    )

    if run_remote:
        # FastMCP v3 uses run(transport=...) for HTTP/SSE transports.
        host = os.getenv("HOST", "0.0.0.0")
        port = int(os.getenv("PORT", "8000"))
        transport = os.getenv("MCP_TRANSPORT", "streamable-http")
        path = os.getenv("MCP_PATH", "/mcp")
        logger.info(
            "Starting MCP server in remote mode (%s) on %s:%s%s",
            transport,
            host,
            port,
            path,
        )
        mcp.run(transport=transport, host=host, port=port, path=path)
    else:
        # Run as local stdio server
        logger.info("Starting MCP server in local mode (stdio)...")
        mcp.run()


# Run server if executed directly
if __name__ == "__main__":
    main()
