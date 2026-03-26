"""
Custom Rules Engine - Load and apply user-defined classification rules
"""

import configparser
import os
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class RulesEngine:
    """Load and apply custom classification rules from rules.ini"""

    def __init__(self, rules_path: str = None):
        """
        Initialize rules engine

        Args:
            rules_path: Path to rules.ini file
        """
        if rules_path is None:
            # Default path: config/rules.ini
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            rules_path = os.path.join(base_dir, "config", "rules.ini")

        self.rules_path = rules_path
        self.config = configparser.ConfigParser()
        self.rules_loaded = False

        self._load_rules()

    def _load_rules(self):
        """Load rules from INI file"""
        if not os.path.exists(self.rules_path):
            logger.warning(f"Rules file not found: {self.rules_path}")
            return

        try:
            self.config.read(self.rules_path)
            self.rules_loaded = True
            logger.info(f"Loaded custom rules from: {self.rules_path}")
        except Exception as e:
            logger.error(f"Error loading rules: {e}")
            self.rules_loaded = False

    def check_sender(self, sender: str) -> Optional[str]:
        """
        Check if sender matches any rule

        Args:
            sender: Email sender address

        Returns:
            Category if matched, None otherwise
        """
        sender_lower = sender.lower()

        # Check each category
        for category in ["senders_urgent", "senders_important", "senders_normal", "senders_spam"]:
            if self.config.has_section(category):
                for rule_sender in self.config.options(category):
                    if rule_sender.lower() in sender_lower:
                        category_name = category.replace("senders_", "").upper()
                        logger.debug(f"Sender rule matched: {sender} -> {category_name}")
                        return category_name

        return None

    def check_subject(self, subject: str) -> Optional[str]:
        """
        Check if subject matches any rule

        Args:
            subject: Email subject

        Returns:
            Category if matched, None otherwise
        """
        subject_lower = subject.lower()

        # Check each category
        for category in ["subject_urgent", "subject_important", "subject_normal", "subject_spam"]:
            if self.config.has_section(category):
                for keyword in self.config.options(category):
                    if keyword.lower() in subject_lower:
                        category_name = category.replace("subject_", "").upper()
                        logger.debug(f"Subject rule matched: '{subject}' contains '{keyword}' -> {category_name}")
                        return category_name

        return None

    def check_domain(self, sender: str) -> Optional[str]:
        """
        Check if sender's domain matches any rule

        Args:
            sender: Email sender address

        Returns:
            Category if matched, None otherwise
        """
        try:
            # Extract domain from sender
            if "@" in sender:
                domain = sender.split("@")[-1].lower()

                # Check each category
                for category in ["domains_urgent", "domains_important", "domains_normal", "domains_spam"]:
                    if self.config.has_section(category):
                        for rule_domain in self.config.options(category):
                            if rule_domain.lower() == domain or rule_domain.lower() in domain:
                                category_name = category.replace("domains_", "").upper()
                                logger.debug(f"Domain rule matched: {domain} -> {category_name}")
                                return category_name
        except Exception as e:
            logger.error(f"Error checking domain: {e}")

        return None

    def get_time_rules(self) -> dict:
        """Get time-based rules"""
        rules = {
            "after_hours_start": 18,  # 6 PM
            "after_hours_end": 9,     # 9 AM
            "weekend_mode": "silent",
        }

        if self.config.has_section("time_rules"):
            try:
                rules["after_hours_start"] = self.config.getint("time_rules", "after_hours_start", fallback=18)
                rules["after_hours_end"] = self.config.getint("time_rules", "after_hours_end", fallback=9)
                rules["weekend_mode"] = self.config.get("time_rules", "weekend_mode", fallback="silent")
            except Exception as e:
                logger.error(f"Error parsing time rules: {e}")

        return rules

    def classify_with_rules(self, email_data: Dict) -> Tuple[Optional[str], str]:
        """
        Classify email using custom rules

        Args:
            email_data: Dictionary with subject, sender, body

        Returns:
            Tuple of (category, reason) or (None, "no_match")
        """
        sender = email_data.get("sender", "")
        subject = email_data.get("subject", "")

        # Check rules in priority order
        # 1. Sender (most specific)
        category = self.check_sender(sender)
        if category:
            return category, f"Sender rule matched: {sender}"

        # 2. Domain
        category = self.check_domain(sender)
        if category:
            return category, f"Domain rule matched: {sender.split('@')[-1]}"

        # 3. Subject keywords
        category = self.check_subject(subject)
        if category:
            return category, f"Subject rule matched: '{subject}' contains keyword"

        return None, "no_match"

    def reload_rules(self):
        """Reload rules from file"""
        self._load_rules()
        logger.info("Rules reloaded")

    def is_loaded(self) -> bool:
        """Check if rules are loaded"""
        return self.rules_loaded
