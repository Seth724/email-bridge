"""
Scheduled Email Checker

Runs the email bot on a schedule using APScheduler.
Defaults to 7 AM daily (configurable via environment variables).
"""

import os
import sys
from dotenv import load_dotenv
from apscheduler.schedulers.blocking import BlockingScheduler
import logging

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from standalone.bot import check_and_notify
from standalone.weekly_summary import send_weekly_summary

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    """Start the scheduled email checker"""

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

    # Get schedule from environment
    hour = int(os.getenv("SCHEDULE_HOUR", "7"))
    minute = int(os.getenv("SCHEDULE_MINUTE", "0"))
    timezone = os.getenv("TIMEZONE", "UTC")

    logger.info(f"Starting scheduler: {hour}:{minute:02d} {timezone}")

    # Create scheduler
    scheduler = BlockingScheduler(timezone=timezone)

    # Add job: run check_and_notify daily
    scheduler.add_job(
        check_and_notify,
        trigger="cron",
        hour=hour,
        minute=minute,
        id="daily_email_check",
        replace_existing=True,
    )

    # Add job: send weekly summary every Sunday at 8 PM
    scheduler.add_job(
        send_weekly_summary,
        trigger="cron",
        day_of_week="sun",
        hour=20,
        minute=0,
        id="weekly_summary",
        replace_existing=True,
    )

    # Add job: send test message on startup
    logger.info("Sending test message...")
    try:
        from core.telegram import TelegramSender

        telegram = TelegramSender()
        telegram.send_test_message()
    except Exception as e:
        logger.error(f"Failed to send test message: {e}")

    logger.info(
        f"Scheduler started! Next run: {hour}:{minute:02d} {timezone}\n"
        f"Weekly summary: Every Sunday at 8:00 PM\n"
        f"Press Ctrl+C to stop."
    )

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped")


if __name__ == "__main__":
    main()
