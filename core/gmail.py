"""
Gmail IMAP Fetcher

Fetches emails from Gmail using IMAP protocol with app password authentication.
No OAuth required - simple and privacy-friendly!
"""

import imaplib
import email
from email.header import decode_header
from email import message as email_message
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class GmailFetcher:
    """Fetch emails from Gmail via IMAP"""

    def __init__(
        self,
        email_address: str,
        app_password: str,
        imap_server: str = "imap.gmail.com",
        imap_port: int = 993,
    ):
        """
        Initialize Gmail fetcher

        Args:
            email_address: Your Gmail address
            app_password: Gmail app password (16 chars)
            imap_server: Gmail IMAP server
            imap_port: IMAP port (default 993 for SSL)
        """
        self.email_address = email_address
        self.app_password = app_password
        self.imap_server = imap_server
        self.imap_port = imap_port
        self.mail = None

    def connect(self) -> bool:
        """Connect to Gmail IMAP server"""
        try:
            self.mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            self.mail.login(self.email_address, self.app_password)
            logger.info(f"Connected to Gmail: {self.email_address}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Gmail: {e}")
            return False

    def disconnect(self):
        """Disconnect from Gmail"""
        if self.mail:
            try:
                self.mail.logout()
                logger.info("Disconnected from Gmail")
            except Exception as e:
                logger.error(f"Error disconnecting: {e}")
            finally:
                self.mail = None

    def fetch_unread_emails(
        self, limit: int = 10, days_back: int = 1
    ) -> List[Dict[str, str]]:
        """
        Fetch unread emails from inbox

        Args:
            limit: Maximum number of emails to fetch
            days_back: Only fetch emails from last N days

        Returns:
            List of email dictionaries with subject, sender, body, etc.
        """
        emails_list = []

        try:
            # Connect if not already connected
            if not self.mail:
                if not self.connect():
                    return []

            # Select inbox
            self.mail.select("inbox")

            # Calculate date threshold
            date_threshold = (datetime.now() - timedelta(days=days_back)).strftime(
                "%d-%b-%Y"
            )

            # Search for unread emails since date
            search_criteria = f'(UNSEEN SINCE "{date_threshold}")'
            result, data = self.mail.search(None, search_criteria)

            if result != "OK":
                logger.error("Failed to search emails")
                return []

            # Get email IDs
            email_ids = data[0].split()
            logger.info(f"Found {len(email_ids)} unread emails")

            # Limit the number of emails
            email_ids = email_ids[-limit:] if len(email_ids) > limit else email_ids

            # Fetch each email
            for email_id in reversed(email_ids):  # Newest first
                email_data = self._fetch_email(email_id)
                if email_data:
                    emails_list.append(email_data)

            return emails_list

        except Exception as e:
            logger.error(f"Error fetching emails: {e}")
            return []

    def _fetch_email(self, email_id: bytes) -> Optional[Dict[str, str]]:
        """Fetch a single email by ID"""
        try:
            result, msg_data = self.mail.fetch(email_id, "(RFC822)")

            if result != "OK":
                return None

            # Parse email
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)

            # Extract subject
            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding or "utf-8", errors="ignore")

            # Extract sender
            from_header = msg.get("From", "")
            sender, encoding = decode_header(from_header)[0]
            if isinstance(sender, bytes):
                sender = sender.decode(encoding or "utf-8", errors="ignore")

            # Extract date
            date_header = msg.get("Date", "")
            date_str = email.utils.parsedate_to_datetime(date_header).isoformat()

            # Extract body (plain text or HTML)
            body = self._get_email_body(msg)

            return {
                "id": email_id.decode(),
                "subject": subject,
                "sender": sender,
                "date": date_str,
                "body": body,
                "raw_date": date_header,
            }

        except Exception as e:
            logger.error(f"Error parsing email: {e}")
            return None

    def _get_email_body(self, msg: email_message.Message) -> str:
        """Extract body text from email"""
        body = ""

        # Walk through email parts
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition", ""))

                # Skip attachments
                if "attachment" in content_disposition:
                    continue

                # Prefer plain text, fallback to HTML
                if content_type == "text/plain" and not body:
                    try:
                        charset = part.get_content_charset() or "utf-8"
                        body = part.get_payload(decode=True).decode(
                            charset, errors="ignore"
                        )
                    except Exception:
                        pass
                elif content_type == "text/html" and not body:
                    try:
                        charset = part.get_content_charset() or "utf-8"
                        html = part.get_payload(decode=True).decode(
                            charset, errors="ignore"
                        )
                        # Simple HTML to text conversion
                        import html2text

                        body = html2text.html2text(html)
                    except Exception:
                        pass
        else:
            # Not multipart
            try:
                charset = msg.get_content_charset() or "utf-8"
                body = msg.get_payload(decode=True).decode(charset, errors="ignore")
            except Exception:
                pass

        # Clean up body
        body = body.strip()[:2000]  # Limit length for AI processing
        return body

    def mark_as_read(self, email_id: str):
        """Mark email as read"""
        try:
            if self.mail:
                self.mail.store(email_id.encode(), "+FLAGS", "\\Seen")
                logger.info(f"Marked email {email_id} as read")
        except Exception as e:
            logger.error(f"Error marking email as read: {e}")

    def get_email_count(self, unread_only: bool = True) -> int:
        """Get count of emails in inbox"""
        try:
            if not self.mail:
                if not self.connect():
                    return 0

            self.mail.select("inbox")

            if unread_only:
                result, data = self.mail.search(None, "UNSEEN")
            else:
                result, data = self.mail.search(None, "ALL")

            if result == "OK":
                return len(data[0].split())
            return 0

        except Exception as e:
            logger.error(f"Error getting email count: {e}")
            return 0
