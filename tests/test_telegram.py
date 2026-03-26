"""
Test Telegram Sender

Run with: pytest tests/test_telegram.py
"""

import os
import pytest
from dotenv import load_dotenv

load_dotenv()


@pytest.fixture
def telegram_sender():
    from core.telegram import TelegramSender

    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not bot_token or not chat_id:
        pytest.skip("TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set")

    return TelegramSender(bot_token=bot_token, chat_id=chat_id)


def test_send_message(telegram_sender):
    """Test sending a basic message"""
    text = "🧪 Test message from pytest"

    result = telegram_sender.send_message(text)

    assert result is True


def test_send_test_message(telegram_sender):
    """Test sending test message"""
    result = telegram_sender.send_test_message()

    assert result is True


def test_send_urgent_alert(telegram_sender):
    """Test sending urgent alert"""
    result = telegram_sender.send_urgent_alert(
        subject="Test Urgent Email",
        sender="Test Sender <test@example.com>",
        summary="This is a test urgent email summary.",
        action="Review and respond",
    )

    assert result is True


def test_send_daily_digest(telegram_sender):
    """Test sending daily digest"""
    result = telegram_sender.send_daily_digest(
        urgent_count=2,
        important_count=3,
        summary_text="📧 Test digest summary",
    )

    assert result is True


def test_get_bot_info(telegram_sender):
    """Test getting bot info"""
    bot_info = telegram_sender.get_me()

    assert bot_info is not None
    assert "username" in bot_info
    assert "first_name" in bot_info


def test_send_with_buttons(telegram_sender):
    """Test sending message with inline buttons"""
    text = "🔘 Test message with buttons"

    buttons = [
        [{"text": "📧 Open Gmail", "url": "https://gmail.com"}],
        [{"text": "✅ Mark as Read", "callback_data": "mark_read"}],
    ]

    result = telegram_sender.send_with_buttons(text, buttons)

    assert result is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
