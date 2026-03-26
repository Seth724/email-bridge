"""
Email Classifier using Groq AI

Classifies emails into categories: URGENT, IMPORTANT, NORMAL, SPAM
Uses Groq's fast LLM API for intelligent classification.
"""

import os
import json
from typing import Dict, List, Optional, Literal
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from langsmith import traceable
import logging

logger = logging.getLogger(__name__)

# Email categories
EmailCategory = Literal["URGENT", "IMPORTANT", "NORMAL", "SPAM"]


class EmailClassifier:
    """Classify emails using Groq AI"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "llama-3.3-70b-versatile",
        temperature: float = 0.1,
        use_custom_rules: bool = True,
    ):
        """
        Initialize email classifier

        Args:
            api_key: Groq API key (or set GROQ_API_KEY env var)
            model: Groq model to use
            temperature: Model temperature (lower = more deterministic)
            use_custom_rules: Whether to use custom rules from rules.ini
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.model = model
        self.temperature = temperature
        self.use_custom_rules = use_custom_rules

        if not self.api_key:
            raise ValueError(
                "Groq API key not provided. Set GROQ_API_KEY env var or pass api_key parameter."
            )

        # Initialize Groq LLM via LangChain
        self.llm = ChatGroq(
            api_key=self.api_key,
            model=self.model,
            temperature=temperature,
        )

        # Load custom rules engine
        if use_custom_rules:
            try:
                from core.rules_engine import RulesEngine
                self.rules_engine = RulesEngine()
                if self.rules_engine.is_loaded():
                    logger.info("Custom rules engine loaded")
                else:
                    logger.warning("Custom rules engine not loaded, using AI only")
                    self.rules_engine = None
            except Exception as e:
                logger.warning(f"Failed to load rules engine: {e}")
                self.rules_engine = None
        else:
            self.rules_engine = None

        logger.info(f"EmailClassifier initialized with model: {model}")

    @traceable(run_type="llm")
    def classify_email(self, email_data: Dict[str, str]) -> Dict:
        """
        Classify a single email

        Args:
            email_data: Dictionary with subject, sender, body

        Returns:
            Classification result with category, confidence, reasoning
        """
        # First, check custom rules (if enabled)
        if self.rules_engine:
            category, reason = self.rules_engine.classify_with_rules(email_data)
            if category:
                # Rule matched, return immediately
                logger.info(f"Custom rule matched: {reason}")
                return {
                    "category": category,
                    "confidence": 0.9,  # High confidence for rule-based
                    "reasoning": f"Custom rule: {reason}",
                    "action_needed": self._get_default_action(category),
                    "summary": email_data.get("subject", "")[:100],
                    "email_subject": email_data.get("subject", ""),
                    "email_sender": email_data.get("sender", ""),
                    "source": "custom_rule",
                }

        # No rule matched, use AI classification
        # Build prompt
        system_prompt = self._get_system_prompt()
        user_prompt = self._build_user_prompt(email_data)

        # Call LLM
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]

        try:
            response = self.llm.invoke(messages)
            result = self._parse_response(response.content)

            # Add original email info
            result["email_subject"] = email_data.get("subject", "")
            result["email_sender"] = email_data.get("sender", "")
            result["source"] = "ai_classification"

            logger.info(
                f"Classified email: '{email_data.get('subject', '')}' as {result['category']}"
            )
            return result

        except Exception as e:
            logger.error(f"Error classifying email: {e}")
            # Fallback to NORMAL category
            return {
                "category": "NORMAL",
                "confidence": 0.5,
                "reasoning": f"Classification error: {str(e)}",
                "email_subject": email_data.get("subject", ""),
                "email_sender": email_data.get("sender", ""),
                "source": "fallback",
            }

    @traceable(run_type="llm")
    def classify_batch(
        self, emails: List[Dict[str, str]]
    ) -> List[Dict]:
        """
        Classify multiple emails

        Args:
            emails: List of email dictionaries

        Returns:
            List of classification results
        """
        results = []
        for email in emails:
            result = self.classify_email(email)
            results.append(result)
        return results

    def _get_system_prompt(self) -> str:
        """Get the system prompt for email classification"""
        return """You are an intelligent email triage assistant. Your job is to classify emails into one of four categories:

**URGENT**: Requires immediate attention (within hours)
- Flight delays, cancellations, or schedule changes
- Job offers, interview invitations, or recruiter messages
- Bank alerts about suspicious activity, fraud, or account issues
- Medical appointments, test results, or health emergencies
- Family emergencies or urgent personal messages
- Server outages, security breaches, or critical system alerts
- Legal notices, court dates, or deadline warnings

**IMPORTANT**: Should be read today but not urgent
- Meeting invitations or calendar updates
- Project updates from colleagues or managers
- Payment confirmations, invoices, or receipts
- Newsletter from important sources (industry news, updates)
- Product shipping confirmifications or delivery updates
- Social media notifications from close connections

**NORMAL**: Regular emails that can wait
- General newsletters and marketing emails
- Social media notifications
- Automated notifications (password changes you initiated, etc.)
- Routine updates and announcements

**SPAM**: Should be ignored or deleted
- Obvious promotional spam
- Phishing attempts
- Get-rich-quick schemes
- Suspicious lottery or inheritance notifications
- Unsolicited business proposals

Respond in JSON format with this structure:
{
    "category": "URGENT|IMPORTANT|NORMAL|SPAM",
    "confidence": 0.0-1.0,
    "reasoning": "Brief explanation of why you chose this category",
    "action_needed": "What action the user should take (if any)",
    "summary": "2-3 sentence summary of the email"
}

Be conservative with URGENT classifications. Only mark truly time-sensitive emails as URGENT."""

    def _get_default_action(self, category: str) -> str:
        """Get default action for a category"""
        actions = {
            "URGENT": "Review immediately",
            "IMPORTANT": "Review today",
            "NORMAL": "Review when convenient",
            "SPAM": "Delete or ignore",
        }
        return actions.get(category, "Review")

    def _build_user_prompt(self, email_data: Dict[str, str]) -> str:
        """Build the user prompt from email data"""
        subject = email_data.get("subject", "No Subject")
        sender = email_data.get("sender", "Unknown Sender")
        body = email_data.get("body", "")[:1500]  # Limit body length

        return f"""Classify this email:

FROM: {sender}
SUBJECT: {subject}

BODY:
{body}

Respond in JSON format."""

    def _parse_response(self, response_text: str) -> Dict:
        """Parse LLM response into structured format"""
        try:
            # Try to extract JSON from response
            import re

            # Find JSON in response (might be wrapped in markdown)
            json_match = re.search(r"```(?:json)?\s*({.*?})\s*```", response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Try to parse entire response as JSON
                json_str = response_text

            result = json.loads(json_str)

            # Validate required fields
            required_fields = ["category", "confidence", "reasoning"]
            for field in required_fields:
                if field not in result:
                    raise ValueError(f"Missing required field: {field}")

            # Validate category
            valid_categories = ["URGENT", "IMPORTANT", "NORMAL", "SPAM"]
            if result["category"] not in valid_categories:
                logger.warning(
                    f"Invalid category '{result['category']}', defaulting to NORMAL"
                )
                result["category"] = "NORMAL"

            # Validate confidence
            if not isinstance(result["confidence"], (int, float)):
                result["confidence"] = 0.5
            result["confidence"] = max(0.0, min(1.0, result["confidence"]))

            return result

        except Exception as e:
            logger.error(f"Error parsing LLM response: {e}")
            # Return fallback
            return {
                "category": "NORMAL",
                "confidence": 0.5,
                "reasoning": f"Failed to parse response: {str(e)}",
                "action_needed": "Review manually",
                "summary": "Classification failed",
            }

    def get_urgent_summary(self, classified_emails: List[Dict]) -> str:
        """
        Generate a summary of urgent emails

        Args:
            classified_emails: List of classified email results

        Returns:
            Formatted summary string
        """
        urgent = [e for e in classified_emails if e["category"] == "URGENT"]
        important = [e for e in classified_emails if e["category"] == "IMPORTANT"]

        summary = "📧 **Email Briefing**\n\n"

        if urgent:
            summary += "🚨 **URGENT** ({count}):\n".format(count=len(urgent))
            for email in urgent:
                summary += f"• {email['email_subject']} (from {email['email_sender']})\n"
                summary += f"  _{email['summary']}_\n"
                summary += f"  **Action**: {email.get('action_needed', 'Review')}\n\n"

        if important:
            summary += "📌 **IMPORTANT** ({count}):\n".format(count=len(important))
            for email in important:
                summary += f"• {email['email_subject']} (from {email['email_sender']})\n"

        if not urgent and not important:
            summary += "✅ No urgent or important emails. All caught up!"

        return summary
