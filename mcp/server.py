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
from workflows.triage_graph import EmailTriageWorkflow

# Initialize FastMCP server
mcp = FastMCP(
    "Email Bridge",
    instructions="""
    Email Bridge MCP Server - Intelligent email triage and notifications.
    
    Tools available:
    - check_emails: Fetch and classify unread emails
    - get_urgent_summary: Get summary of urgent emails only
    - send_telegram_message: Send a message to Telegram
    - test_connection: Test Gmail and Telegram connections
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


# Run server if executed directly
if __name__ == "__main__":
    import sys
    
    # Check if running as remote server
    if len(sys.argv) > 1 and sys.argv[1] == "--remote":
        # Run as HTTP SSE server for remote deployment
        logger.info("Starting MCP server in remote mode (SSE)...")
        mcp.run_sse(host="0.0.0.0", port=8000)
    else:
        # Run as local stdio server
        logger.info("Starting MCP server in local mode (stdio)...")
        mcp.run()
