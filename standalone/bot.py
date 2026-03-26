"""
Standalone Telegram Bot

Checks emails and sends notifications to Telegram.
Can be run manually or on a schedule.
"""

import os
import sys
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.gmail import GmailFetcher
from core.classifier import EmailClassifier
from core.telegram import TelegramSender
from core.time_urgency import TimeUrgencyManager
from workflows.triage_graph import EmailTriageWorkflow

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def check_and_notify():
    """
    Main function: Check emails and send Telegram notifications
    """
    logger.info("Starting email check...")

    try:
        # Validate required environment variables
        required_vars = {
            "GMAIL_ADDRESS": "Gmail address",
            "GMAIL_APP_PASSWORD": "Gmail app password",
            "GROQ_API_KEY": "Groq API key",
            "TELEGRAM_BOT_TOKEN": "Telegram bot token",
            "TELEGRAM_CHAT_ID": "Telegram chat ID",
        }
        
        missing_vars = []
        for var, desc in required_vars.items():
            if not os.getenv(var):
                missing_vars.append(f"  - {var}: {desc}")
        
        if missing_vars:
            logger.error("Missing required environment variables:")
            for var in missing_vars:
                logger.error(var)
            logger.error("\nPlease set these variables in your .env file or environment.")
            return

        # Initialize components
        gmail = GmailFetcher(
            email_address=os.getenv("GMAIL_ADDRESS"),
            app_password=os.getenv("GMAIL_APP_PASSWORD"),
        )

        classifier = EmailClassifier(
            api_key=os.getenv("GROQ_API_KEY"),
            model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
        )

        telegram = TelegramSender(
            bot_token=os.getenv("TELEGRAM_BOT_TOKEN"),
            chat_id=os.getenv("TELEGRAM_CHAT_ID"),
        )

        time_manager = TimeUrgencyManager.from_env()

        # Fetch unread emails (last 10, from past 1 day)
        emails = gmail.fetch_unread_emails(limit=10, days_back=1)
        logger.info(f"Fetched {len(emails)} unread emails")

        if not emails:
            logger.info("No unread emails found")
            return

        # Process through LangGraph workflow
        workflow = EmailTriageWorkflow(classifier)
        result = workflow.process_emails(emails)

        logger.info(
            f"Classification complete: {len(result['urgent_emails'])} urgent, "
            f"{len(result['important_emails'])} important"
        )

        # Track notified emails
        notified_email_ids = []
        notified_urgent = 0
        notified_important = 0

        # Send urgent alerts immediately (with sound if not quiet hours)
        for email in result["urgent_emails"]:
            # Check time-based rules
            mode = time_manager.get_notification_mode("URGENT")
            
            if mode["send"]:
                telegram.send_urgent_alert(
                    subject=email["email_subject"],
                    sender=email["email_sender"],
                    summary=email["summary"],
                    action=email.get("action_needed", "Review email"),
                    email_id=email.get("email_id"),  # Pass email_id for buttons
                )
                notified_email_ids.append(email.get("email_id"))
                notified_urgent += 1
                logger.info(f"Sent URGENT alert: {email['email_subject']}")
            else:
                logger.info(f"Skipped URGENT notification (time rules): {email['email_subject']}")

        # Send important emails (silent if during quiet hours)
        for email in result["important_emails"]:
            mode = time_manager.get_notification_mode("IMPORTANT")
            
            if mode["send"]:
                # Send as part of digest (silent)
                notified_important += 1
                logger.info(f"Counted IMPORTANT: {email['email_subject']}")
            else:
                logger.info(f"Skipped IMPORTANT notification (time rules): {email['email_subject']}")

        # Send daily digest if there are important emails
        if notified_important > 0 or notified_urgent > 0:
            telegram.send_daily_digest(
                urgent_count=notified_urgent,
                important_count=notified_important,
                summary_text=result["summary"],
            )
        else:
            # Send "all clear" message only if not in quiet hours
            if not time_manager.is_quiet_hours():
                telegram.send_message("✅ No important emails. Inbox is clear!")

        # Mark processed emails as read (prevents duplicates on next run)
        for email in emails:
            try:
                gmail.mark_as_read(email["id"])
                logger.debug(f"Marked email {email['id']} as read")
            except Exception as e:
                logger.warning(f"Failed to mark email as read: {e}")

        logger.info(f"Email check completed. Notified about {len(notified_email_ids)} emails.")

    except Exception as e:
        logger.error(f"Error in email check: {e}", exc_info=True)
        # Send error notification
        try:
            telegram = TelegramSender()
            telegram.send_message(f"❌ Email Bridge Error:\n\n{str(e)}")
        except Exception:
            pass

    finally:
        # Cleanup
        if "gmail" in locals():
            gmail.disconnect()


if __name__ == "__main__":
    check_and_notify()
