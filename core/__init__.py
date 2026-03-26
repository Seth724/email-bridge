"""
Email Bridge - Core Module

This module provides the core functionality for email classification
and Telegram notification.
"""

from .gmail import GmailFetcher
from .classifier import EmailClassifier
from .telegram import TelegramSender

__all__ = ["GmailFetcher", "EmailClassifier", "TelegramSender"]
