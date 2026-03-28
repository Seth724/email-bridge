"""
Telegram Webhook Handler

Handles callback queries from Telegram inline buttons.
Processes actions like mark as read, archive, copy subject, etc.
"""

import os
import logging
from typing import Optional, Dict, Any
from dotenv import load_dotenv

from core.gmail import GmailFetcher
from core.telegram import TelegramSender

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class WebhookHandler:
    """Handle Telegram webhook callbacks from inline buttons"""

    def __init__(self):
        """Initialize webhook handler"""
        self.gmail = GmailFetcher(
            email_address=os.getenv("GMAIL_ADDRESS"),
            app_password=os.getenv("GMAIL_APP_PASSWORD"),
        )
        self.telegram = TelegramSender(
            bot_token=os.getenv("TELEGRAM_BOT_TOKEN"),
            chat_id=os.getenv("TELEGRAM_CHAT_ID"),
        )
        logger.info("WebhookHandler initialized")

    def handle_callback(self, callback_data: str, message_id: int, chat_id: str) -> Dict[str, Any]:
        """
        Handle callback query from Telegram button

        Args:
            callback_data: Data from button (e.g., "mark_read:email_id")
            message_id: ID of the message with buttons
            chat_id: Telegram chat ID

        Returns:
            Dictionary with response action
        """
        try:
            # Parse callback data
            parts = callback_data.split(":", 1)
            action = parts[0]
            param = parts[1] if len(parts) > 1 else None

            logger.info(f"Handling callback: action={action}, param={param}")

            # Connect to Gmail
            if not self.gmail.connect():
                return {
                    "success": False,
                    "answer_text": "❌ Failed to connect to Gmail",
                    "show_alert": True,
                }

            # Route to appropriate handler
            if action == "mark_read":
                result = self._handle_mark_read(param)
            elif action == "archive":
                result = self._handle_archive(param)
            elif action == "copy":
                result = self._handle_copy(param)
            elif action == "mark_unread":
                result = self._handle_mark_unread(param)
            elif action == "delete":
                result = self._handle_delete(param)
            else:
                result = {
                    "success": False,
                    "answer_text": f"❌ Unknown action: {action}",
                    "show_alert": True,
                }

            # Disconnect Gmail
            self.gmail.disconnect()

            return result

        except Exception as e:
            logger.error(f"Error handling callback: {e}")
            return {
                "success": False,
                "answer_text": f"❌ Error: {str(e)}",
                "show_alert": True,
            }

    def _handle_mark_read(self, email_id: str) -> Dict[str, Any]:
        """Handle mark as read action"""
        success = self.gmail.mark_as_read(email_id)

        if success:
            return {
                "success": True,
                "answer_text": "✅ Marked as read",
                "show_alert": False,
            }
        else:
            return {
                "success": False,
                "answer_text": "❌ Failed to mark as read",
                "show_alert": True,
            }

    def _handle_archive(self, email_id: str) -> Dict[str, Any]:
        """Handle archive action"""
        success = self.gmail.archive_email(email_id)

        if success:
            return {
                "success": True,
                "answer_text": "🗑️ Archived",
                "show_alert": False,
            }
        else:
            return {
                "success": False,
                "answer_text": "❌ Failed to archive",
                "show_alert": True,
            }

    def _handle_copy(self, text: str) -> Dict[str, Any]:
        """Handle copy subject action"""
        # Telegram doesn't support direct clipboard access
        # Send the text as a message that user can copy
        return {
            "success": True,
            "answer_text": f"📋 Subject:\n{text}",
            "show_alert": True,  # Show as alert so user can long-press to copy
        }

    def _handle_mark_unread(self, email_id: str) -> Dict[str, Any]:
        """Handle mark as unread action"""
        success = self.gmail.mark_as_unread(email_id)

        if success:
            return {
                "success": True,
                "answer_text": "📧 Marked as unread",
                "show_alert": False,
            }
        else:
            return {
                "success": False,
                "answer_text": "❌ Failed to mark as unread",
                "show_alert": True,
            }

    def _handle_delete(self, email_id: str) -> Dict[str, Any]:
        """Handle delete action"""
        success = self.gmail.delete_email(email_id)

        if success:
            return {
                "success": True,
                "answer_text": "🗑️ Deleted",
                "show_alert": False,
            }
        else:
            return {
                "success": False,
                "answer_text": "❌ Failed to delete",
                "show_alert": True,
            }

    def close(self):
        """Cleanup resources"""
        try:
            self.gmail.disconnect()
        except Exception:
            pass
