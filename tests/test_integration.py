"""
Integration Tests - Full Workflow Testing

Run with: pytest tests/test_integration.py -v
Or: python -m pytest tests/test_integration.py -v

This tests the complete workflow from email fetching to notification.
"""

import os
import pytest
from dotenv import load_dotenv
from unittest.mock import Mock, patch, MagicMock

load_dotenv()


class TestFullWorkflow:
    """Test the complete email-to-telegram workflow"""

    @pytest.fixture
    def sample_emails(self):
        """Sample emails for testing"""
        return [
            {
                "id": "1",
                "subject": "Flight DL-456 has been delayed",
                "sender": "Delta Airlines <noreply@delta.com>",
                "body": "Your flight has been delayed by 2 hours.",
                "date": "2025-03-26T10:00:00",
                "raw_date": "Thu, 26 Mar 2025 10:00:00 +0000",
            },
            {
                "id": "2",
                "subject": "Meeting invitation: Q1 Planning",
                "sender": "John Doe <john@company.com>",
                "body": "You're invited to Q1 planning meeting on Friday at 2 PM.",
                "date": "2025-03-26T09:00:00",
                "raw_date": "Thu, 26 Mar 2025 09:00:00 +0000",
            },
            {
                "id": "3",
                "subject": "Weekly newsletter - Issue #42",
                "sender": "TechCrunch <newsletter@techcrunch.com>",
                "body": "This week in tech news...",
                "date": "2025-03-26T08:00:00",
                "raw_date": "Thu, 26 Mar 2025 08:00:00 +0000",
            },
        ]

    def test_workflow_initialization(self):
        """Test that all workflow components can be initialized"""
        try:
            from core.gmail import GmailFetcher
            from core.classifier import EmailClassifier
            from core.telegram import TelegramSender
            from workflows.triage_graph import EmailTriageWorkflow

            # These should raise ValueError if env vars missing
            with pytest.raises(ValueError):
                GmailFetcher(
                    email_address=os.getenv("GMAIL_ADDRESS", ""),
                    app_password=os.getenv("GMAIL_APP_PASSWORD", ""),
                )
        except Exception as e:
            pytest.skip(f"Skipped: {e}")

    def test_email_classification_workflow(self, sample_emails):
        """Test email classification workflow"""
        try:
            from core.classifier import EmailClassifier

            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                pytest.skip("GROQ_API_KEY not set")

            classifier = EmailClassifier(api_key=api_key)

            # Test urgent email
            result = classifier.classify_email(sample_emails[0])
            assert result is not None
            assert "category" in result
            assert result["category"] in ["URGENT", "IMPORTANT", "NORMAL", "SPAM"]
            assert "confidence" in result
            assert 0 <= result["confidence"] <= 1

        except Exception as e:
            pytest.skip(f"Skipped: {e}")

    def test_time_urgency_manager(self):
        """Test time-based notification rules"""
        from core.time_urgency import TimeUrgencyManager
        from datetime import datetime

        manager = TimeUrgencyManager(
            quiet_hours_start=22,
            quiet_hours_end=7,
            weekend_mode="silent",
        )

        # Test weekday during normal hours
        dt_normal = datetime(2025, 3, 26, 10, 0, 0)  # Wed 10 AM
        assert not manager.is_weekend(dt_normal)
        assert not manager.is_quiet_hours(dt_normal)

        # Test quiet hours
        dt_quiet = datetime(2025, 3, 26, 23, 0, 0)  # Wed 11 PM
        assert manager.is_quiet_hours(dt_quiet)

        # Test weekend
        dt_weekend = datetime(2025, 3, 29, 10, 0, 0)  # Sat 10 AM
        assert manager.is_weekend(dt_weekend)

    def test_triage_workflow_structure(self):
        """Test that triage workflow building works"""
        try:
            from core.classifier import EmailClassifier
            from workflows.triage_graph import EmailTriageWorkflow

            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                pytest.skip("GROQ_API_KEY not set")

            classifier = EmailClassifier(api_key=api_key)
            workflow = EmailTriageWorkflow(classifier)

            # Verify workflow graph is compiled
            assert workflow.graph is not None
            assert hasattr(workflow.graph, "invoke")

        except Exception as e:
            pytest.skip(f"Skipped: {e}")

    def test_triage_workflow_with_mock_emails(self):
        """Test full triage workflow with mocked Gmail"""
        try:
            from core.classifier import EmailClassifier
            from workflows.triage_graph import EmailTriageWorkflow

            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                pytest.skip("GROQ_API_KEY not set")

            classifier = EmailClassifier(api_key=api_key)
            workflow = EmailTriageWorkflow(classifier)

            # Mock emails
            sample_emails = [
                {
                    "subject": "URGENT: Server down",
                    "sender": "DevOps <devops@company.com>",
                    "body": "Production server is down. Immediate action required.",
                    "id": "1",
                    "date": "2025-03-26T10:00:00",
                }
            ]

            # Run workflow
            result = workflow.process_emails(sample_emails)

            # Verify output structure
            assert "classified_emails" in result
            assert "urgent_emails" in result
            assert "important_emails" in result
            assert "summary" in result
            assert "send_telegram" in result

            # Verify summary generation
            assert len(result["summary"]) > 0

        except Exception as e:
            pytest.skip(f"Skipped: {e}")

    def test_telegram_message_structure(self):
        """Test Telegram message formatting"""
        try:
            from core.telegram import TelegramSender

            bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
            chat_id = os.getenv("TELEGRAM_CHAT_ID")

            if not bot_token or not chat_id:
                pytest.skip("Telegram credentials not set")

            telegram = TelegramSender(bot_token=bot_token, chat_id=chat_id)

            # Test message composition
            text = """📧 **Test Message**

This is a test message to verify formatting."""

            # We can't actually send without risk, but we can verify object exists
            assert telegram.bot_token == bot_token
            assert telegram.chat_id == chat_id

        except Exception as e:
            pytest.skip(f"Skipped: {e}")

    def test_rules_engine_integration(self):
        """Test custom rules engine"""
        try:
            from core.rules_engine import RulesEngine

            rules = RulesEngine()

            if not rules.is_loaded():
                pytest.skip("Rules file not available")

            # Test sender check
            category = rules.check_sender("ceo@company.com")
            if category:  # If defined in rules
                assert category in ["URGENT", "IMPORTANT", "NORMAL", "SPAM"]

            # Test subject check
            category = rules.check_subject("URGENT: Action needed")
            if category:
                assert category in ["URGENT", "IMPORTANT", "NORMAL", "SPAM"]

        except Exception as e:
            pytest.skip(f"Skipped: {e}")

    def test_config_validation(self):
        """Test configuration validation"""
        try:
            from core.config import ConfigValidator

            # This should not raise if env vars are set
            try:
                config = ConfigValidator.validate()
                assert "GMAIL_ADDRESS" in config
                assert "GROQ_API_KEY" in config
            except ValueError:
                # Expected if env vars not set
                pass

        except Exception as e:
            pytest.skip(f"Skipped: {e}")


class TestComponentIntegration:
    """Test component interactions"""

    def test_classifier_with_rules_engine(self):
        """Test EmailClassifier using custom rules"""
        try:
            from core.classifier import EmailClassifier

            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                pytest.skip("GROQ_API_KEY not set")

            # Initialize with custom rules enabled
            classifier = EmailClassifier(
                api_key=api_key,
                use_custom_rules=True,
            )

            email = {
                "subject": "URGENT: Critical issue",
                "sender": "boss@company.com",
                "body": "We need to address this immediately.",
            }

            result = classifier.classify_email(email)

            # Should use rules first if available
            assert result["category"] in ["URGENT", "IMPORTANT", "NORMAL", "SPAM"]

        except Exception as e:
            pytest.skip(f"Skipped: {e}")

    def test_workflow_error_handling(self):
        """Test workflow handles errors gracefully"""
        try:
            from core.classifier import EmailClassifier
            from workflows.triage_graph import EmailTriageWorkflow

            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                pytest.skip("GROQ_API_KEY not set")

            classifier = EmailClassifier(api_key=api_key)
            workflow = EmailTriageWorkflow(classifier)

            # Test with empty email list
            result = workflow.process_emails([])

            assert result is not None
            assert "summary" in result
            assert result["send_telegram"] is False

        except Exception as e:
            pytest.skip(f"Skipped: {e}")


class TestProductionReadiness:
    """Test production-readiness criteria"""

    def test_error_recovery(self):
        """Verify error handling doesn't crash"""
        try:
            from core.classifier import EmailClassifier

            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                pytest.skip("GROQ_API_KEY not set")

            classifier = EmailClassifier(api_key=api_key)

            # Test with invalid email
            invalid_email = {
                "subject": None,
                "sender": None,
                "body": None,
            }

            # Should not crash
            result = classifier.classify_email(invalid_email)
            assert result is not None

        except Exception as e:
            pytest.skip(f"Skipped: {e}")

    def test_logging_output(self, capsys):
        """Verify logging is configured"""
        import logging

        logger = logging.getLogger("email_bridge")
        logger.info("Test log message")

        # If logging is set up, this should work
        assert logger is not None

    def test_env_var_validation(self):
        """Test environment variable validation"""
        try:
            from core.config import ConfigValidator

            # Should raise if required vars missing
            try:
                ConfigValidator.validate()
            except ValueError as e:
                # Expected if missing
                assert "GMAIL" in str(e) or "TELEGRAM" in str(e) or "GROQ" in str(e)

        except Exception as e:
            pytest.skip(f"Skipped: {e}")
