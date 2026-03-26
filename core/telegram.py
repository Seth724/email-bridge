"""
Telegram Sender

Sends notifications and summaries to Telegram using the Bot API.
Supports both aiogram and python-telegram-bot libraries.
"""

import os
import logging
from typing import Optional
import requests

logger = logging.getLogger(__name__)


class TelegramSender:
    """Send messages to Telegram via Bot API"""

    def __init__(
        self,
        bot_token: Optional[str] = None,
        chat_id: Optional[str] = None,
    ):
        """
        Initialize Telegram sender

        Args:
            bot_token: Telegram bot token from @BotFather
            chat_id: Your Telegram chat ID
        """
        self.bot_token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID")

        if not self.bot_token:
            raise ValueError(
                "Telegram bot token not provided. Set TELEGRAM_BOT_TOKEN env var."
            )

        if not self.chat_id:
            raise ValueError(
                "Telegram chat ID not provided. Set TELEGRAM_CHAT_ID env var."
            )

        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"

        logger.info(f"TelegramSender initialized for chat: {chat_id}")

    def send_message(
        self,
        text: str,
        parse_mode: str = "Markdown",
        disable_notification: bool = False,
    ) -> bool:
        """
        Send a text message to Telegram

        Args:
            text: Message text (supports Markdown/HTML)
            parse_mode: 'Markdown' or 'HTML'
            disable_notification: Send silently if True

        Returns:
            True if successful, False otherwise
        """
        url = f"{self.base_url}/sendMessage"

        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_notification": disable_notification,
        }

        try:
            response = requests.post(url, json=payload, timeout=10)
            result = response.json()

            if result.get("ok"):
                logger.info(f"Message sent to Telegram: {text[:50]}...")
                return True
            else:
                logger.error(f"Telegram API error: {result}")
                return False

        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
            return False

    def send_urgent_alert(
        self,
        subject: str,
        sender: str,
        summary: str,
        action: str,
        email_id: str = None,
    ) -> bool:
        """
        Send an urgent email alert

        Args:
            subject: Email subject
            sender: Email sender
            summary: Email summary
            action: Recommended action
            email_id: Gmail email ID (for buttons)

        Returns:
            True if successful
        """
        text = f"""🚨 **URGENT EMAIL ALERT** 🚨

📧 **Subject**: {subject}
👤 **From**: {sender}

📝 **Summary**:
{summary}

✅ **Action Needed**: {action}

_Open your email to respond._"""

        # Send with buttons if email_id provided
        if email_id:
            return self.send_urgent_alert_with_buttons(text, email_id, subject)
        
        # Send as regular urgent message (with sound)
        return self.send_message(text, parse_mode="Markdown", disable_notification=False)

    def send_urgent_alert_with_buttons(
        self,
        text: str,
        email_id: str,
        subject: str,
    ) -> bool:
        """Send urgent alert with interactive buttons"""
        # Truncate subject for button
        short_subject = subject[:30] + "..." if len(subject) > 30 else subject
        
        buttons = [
            [
                {"text": "📧 Open in Gmail", "url": f"https://mail.google.com/mail/u/0/#inbox/{email_id}"},
                {"text": "✅ Mark as Read", "callback_data": f"mark_read:{email_id}"}
            ],
            [
                {"text": "🗑️ Archive", "callback_data": f"archive:{email_id}"},
                {"text": "📋 Copy Subject", "callback_data": f"copy:{subject}"}
            ]
        ]
        
        return self.send_with_buttons(text, buttons)

    def send_daily_digest(
        self,
        urgent_count: int,
        important_count: int,
        summary_text: str,
    ) -> bool:
        """
        Send daily email digest

        Args:
            urgent_count: Number of urgent emails
            important_count: Number of important emails
            summary_text: Formatted summary

        Returns:
            True if successful
        """
        text = f"""📧 **Daily Email Digest**

🚨 Urgent: {urgent_count}
📌 Important: {important_count}

{summary_text}

_Have a productive day!_"""

        # Send as regular notification (can be silenced)
        return self.send_message(text, parse_mode="Markdown", disable_notification=True)

    def send_test_message(self) -> bool:
        """Send a test message to verify connection"""
        text = """✅ **Email Bridge Test**

Your Telegram integration is working correctly!

You'll now receive:
• 🚨 Urgent email alerts (with sound)
• 📧 Daily digest at 7 AM (silent)

Configure your notification preferences in Telegram."""
        return self.send_message(text, parse_mode="Markdown")

    def get_me(self) -> Optional[dict]:
        """Get bot info"""
        try:
            url = f"{self.base_url}/getMe"
            response = requests.get(url, timeout=10)
            result = response.json()

            if result.get("ok"):
                return result.get("result")
            return None

        except Exception as e:
            logger.error(f"Error getting bot info: {e}")
            return None

    def send_with_buttons(
        self,
        text: str,
        buttons: list,
    ) -> bool:
        """
        Send message with inline keyboard buttons

        Args:
            text: Message text
            buttons: List of button rows, where each row is a list of button dicts
                    [{"text": "Label", "url": "https://..."}, ...]
                    Each row can contain multiple buttons

        Returns:
            True if successful
        """
        url = f"{self.base_url}/sendMessage"

        # Build inline keyboard
        keyboard = []
        
        # Handle both flat list and nested list formats
        if buttons and isinstance(buttons[0], list):
            # Already in row format (list of lists)
            for row in buttons:
                kbd_row = []
                for btn in row:
                    if "url" in btn:
                        kbd_row.append({"text": btn["text"], "url": btn["url"]})
                    elif "callback_data" in btn:
                        kbd_row.append({"text": btn["text"], "callback_data": btn["callback_data"]})
                if kbd_row:
                    keyboard.append(kbd_row)
        else:
            # Flat list format - put each button in its own row
            for btn in buttons:
                row = []
                if "url" in btn:
                    row.append({"text": btn["text"], "url": btn["url"]})
                elif "callback_data" in btn:
                    row.append({"text": btn["text"], "callback_data": btn["callback_data"]})
                if row:
                    keyboard.append(row)

        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "Markdown",
            "reply_markup": {"inline_keyboard": keyboard},
        }

        try:
            response = requests.post(url, json=payload, timeout=10)
            result = response.json()

            if result.get("ok"):
                return True
            else:
                logger.error(f"Telegram API error: {result}")
                return False

        except Exception as e:
            logger.error(f"Error sending message with buttons: {e}")
            return False
