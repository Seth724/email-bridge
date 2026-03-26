"""
Audio Summary - Convert email summaries to voice messages

Uses Google Text-to-Speech (gTTS) to create voice messages.
"""

import os
import tempfile
from typing import Optional
import logging
import requests

logger = logging.getLogger(__name__)


class AudioSummary:
    """Generate and send voice summaries via Telegram"""

    def __init__(self, language: str = "en"):
        """
        Initialize audio summary

        Args:
            language: Language code for TTS (default: English)
        """
        self.language = language
        logger.info(f"AudioSummary initialized (language: {language})")

    def generate_speech(self, text: str) -> Optional[bytes]:
        """
        Generate speech from text using gTTS

        Args:
            text: Text to convert to speech

        Returns:
            MP3 audio data as bytes, or None if failed
        """
        try:
            from gtts import gTTS

            # Create gTTS object
            tts = gTTS(text=text, lang=self.language, slow=False)

            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                temp_path = fp.name
                tts.save(temp_path)

            # Read file
            with open(temp_path, "rb") as f:
                audio_data = f.read()

            # Clean up
            os.unlink(temp_path)

            logger.info(f"Generated speech ({len(audio_data)} bytes)")
            return audio_data

        except ImportError:
            logger.error("gTTS not installed. Run: pip install gTTS")
            return None
        except Exception as e:
            logger.error(f"Error generating speech: {e}")
            return None

    def send_voice_message(
        self,
        bot_token: str,
        chat_id: str,
        audio_data: bytes,
        caption: str = None,
    ) -> bool:
        """
        Send voice message to Telegram

        Args:
            bot_token: Telegram bot token
            chat_id: Chat ID
            audio_data: MP3 audio data
            caption: Optional caption

        Returns:
            True if successful
        """
        url = f"https://api.telegram.org/bot{bot_token}/sendVoice"

        files = {"voice": audio_data}
        data = {"chat_id": chat_id}

        if caption:
            data["caption"] = caption

        try:
            response = requests.post(url, files=files, data=data, timeout=30)
            result = response.json()

            if result.get("ok"):
                logger.info("Voice message sent successfully")
                return True
            else:
                logger.error(f"Telegram API error: {result}")
                return False

        except Exception as e:
            logger.error(f"Error sending voice message: {e}")
            return False

    def send_voice_summary(
        self,
        summary_text: str,
        bot_token: str,
        chat_id: str,
        caption: str = "📧 Your Email Summary",
    ) -> bool:
        """
        Generate and send voice summary

        Args:
            summary_text: Text summary to convert to voice
            bot_token: Telegram bot token
            chat_id: Chat ID
            caption: Caption for voice message

        Returns:
            True if successful
        """
        logger.info("Generating voice summary...")

        # Generate speech
        audio_data = self.generate_speech(summary_text)
        if not audio_data:
            return False

        # Send voice message
        return self.send_voice_message(
            bot_token=bot_token,
            chat_id=chat_id,
            audio_data=audio_data,
            caption=caption,
        )


# Convenience function
def send_voice_summary(summary_text: str) -> bool:
    """
    Send voice summary using environment variables

    Args:
        summary_text: Summary text to convert to speech

    Returns:
        True if successful
    """
    try:
        audio = AudioSummary()

        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")

        if not bot_token or not chat_id:
            logger.error("Telegram credentials not set")
            return False

        return audio.send_voice_summary(
            summary_text=summary_text,
            bot_token=bot_token,
            chat_id=chat_id,
            caption="📧 Your Email Summary",
        )

    except Exception as e:
        logger.error(f"Error in send_voice_summary: {e}")
        return False


if __name__ == "__main__":
    # Test voice summary
    from dotenv import load_dotenv
    load_dotenv()

    test_text = """
    Hello! This is your email summary for today.
    You have 3 urgent emails and 5 important emails.
    The most urgent one is from your boss about the meeting tomorrow.
    Have a great day!
    """

    result = send_voice_summary(test_text)
    print(f"Voice summary sent: {result}")
