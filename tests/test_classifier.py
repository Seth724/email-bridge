"""
Test Email Classifier

Run with: pytest tests/test_classifier.py
"""

import os
import pytest
from dotenv import load_dotenv

load_dotenv()

# Skip tests if no API key
@pytest.fixture
def classifier():
    from core.classifier import EmailClassifier

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        pytest.skip("GROQ_API_KEY not set")

    return EmailClassifier(api_key=api_key, model="llama-3.3-70b-versatile")


def test_classify_urgent_email(classifier):
    """Test classification of urgent email"""
    email = {
        "subject": "Your flight DL-456 has been delayed",
        "sender": "Delta Airlines <notifications@delta.com>",
        "body": """
        Dear Passenger,
        
        Your flight DL-456 from New York to London scheduled for tomorrow 
        at 3:00 PM has been delayed by 2 hours. New departure time: 5:00 PM.
        
        Please arrive at the airport accordingly.
        
        Regards,
        Delta Airlines
        """,
    }

    result = classifier.classify_email(email)

    assert result["category"] == "URGENT"
    assert result["confidence"] > 0.7
    assert "flight" in result["reasoning"].lower() or "delay" in result["reasoning"].lower()


def test_classify_spam_email(classifier):
    """Test classification of spam email"""
    email = {
        "subject": "🎉 CONGRATULATIONS! You've won $1,000,000!!!",
        "sender": "Dr. Smith <winner@lottery-intl.com>",
        "body": """
        Dear Friend,
        
        You have been selected as the winner of our international lottery.
        To claim your $1,000,000 prize, please send your bank details and 
        a processing fee of $500.
        
        Urgent response required!
        
        Dr. Smith
        International Lottery Commission
        """,
    }

    result = classifier.classify_email(email)

    assert result["category"] == "SPAM"
    assert result["confidence"] > 0.8


def test_classify_normal_email(classifier):
    """Test classification of normal email"""
    email = {
        "subject": "Weekly Tech Newsletter - Issue #42",
        "sender": "TechCrunch <newsletter@techcrunch.com>",
        "body": """
        This week in tech:
        
        - New AI model released
        - Startup raises $10M Series A
        - Apple announces new product event
        
        Read more on our website.
        """,
    }

    result = classifier.classify_email(email)

    assert result["category"] == "NORMAL"
    assert result["confidence"] > 0.6


def test_classify_important_email(classifier):
    """Test classification of important email"""
    email = {
        "subject": "Meeting Invitation: Q1 Planning Review",
        "sender": "John Manager <john@company.com>",
        "body": """
        Hi Team,
        
        You're invited to attend the Q1 Planning Review meeting.
        
        Date: Next Monday, 2:00 PM
        Location: Conference Room A / Zoom
        
        Please confirm your attendance.
        
        Best,
        John
        """,
    }

    result = classifier.classify_email(email)

    assert result["category"] == "IMPORTANT"
    assert result["confidence"] > 0.6


def test_parse_json_response(classifier):
    """Test JSON parsing from LLM response"""
    response_text = """
    ```json
    {
        "category": "URGENT",
        "confidence": 0.95,
        "reasoning": "Flight delay requires immediate attention",
        "action_needed": "Check new flight time",
        "summary": "Flight delayed by 2 hours"
    }
    ```
    """

    result = classifier._parse_response(response_text)

    assert result["category"] == "URGENT"
    assert result["confidence"] == 0.95
    assert "Flight" in result["reasoning"]


def test_parse_markdown_json(classifier):
    """Test parsing JSON without markdown wrappers"""
    response_text = """
    {
        "category": "NORMAL",
        "confidence": 0.8,
        "reasoning": "Regular newsletter",
        "action_needed": "Read when convenient",
        "summary": "Weekly tech news"
    }
    """

    result = classifier._parse_response(response_text)

    assert result["category"] == "NORMAL"
    assert result["confidence"] == 0.8


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
