"""
Time-based urgency manager

Handles quiet hours, weekend modes, and time-sensitive notifications.
"""

from datetime import datetime
from typing import Literal
import logging

logger = logging.getLogger(__name__)


class TimeUrgencyManager:
    """Manage time-based notification rules"""

    def __init__(
        self,
        quiet_hours_start: int = 22,
        quiet_hours_end: int = 7,
        weekend_mode: Literal["silent", "normal", "urgent_only"] = "silent",
    ):
        """
        Initialize time urgency manager

        Args:
            quiet_hours_start: Hour when quiet hours start (24h format)
            quiet_hours_end: Hour when quiet hours end
            weekend_mode: How to handle weekends (silent/normal/urgent_only)
        """
        self.quiet_hours_start = quiet_hours_start
        self.quiet_hours_end = quiet_hours_end
        self.weekend_mode = weekend_mode

        logger.info(
            f"TimeUrgencyManager initialized: "
            f"Quiet hours {quiet_hours_start}:00-{quiet_hours_end}:00, "
            f"Weekend mode: {weekend_mode}"
        )

    def is_quiet_hours(self, dt: datetime = None) -> bool:
        """
        Check if current time is within quiet hours

        Args:
            dt: Datetime to check (default: now)

        Returns:
            True if in quiet hours
        """
        if dt is None:
            dt = datetime.now()

        hour = dt.hour

        # Quiet hours span midnight (e.g., 22:00 - 07:00)
        if self.quiet_hours_start > self.quiet_hours_end:
            # Overnight quiet hours
            return hour >= self.quiet_hours_start or hour < self.quiet_hours_end
        else:
            # Same-day quiet hours
            return self.quiet_hours_start <= hour < self.quiet_hours_end

    def is_weekend(self, dt: datetime = None) -> bool:
        """
        Check if date is weekend

        Args:
            dt: Datetime to check

        Returns:
            True if Saturday (5) or Sunday (6)
        """
        if dt is None:
            dt = datetime.now()

        return dt.weekday() >= 5

    def should_send_notification(self, category: str, dt: datetime = None) -> bool:
        """
        Determine if notification should be sent based on time rules

        Args:
            category: Email category (URGENT, IMPORTANT, NORMAL)
            dt: Datetime to check

        Returns:
            True if notification should be sent
        """
        if dt is None:
            dt = datetime.now()

        # Check weekend mode
        if self.is_weekend(dt):
            if self.weekend_mode == "silent":
                logger.debug("Weekend silent mode - no notifications")
                return False
            elif self.weekend_mode == "urgent_only":
                if category != "URGENT":
                    logger.debug(f"Weekend urgent_only mode - skipping {category}")
                    return False

        # Check quiet hours
        if self.is_quiet_hours(dt):
            if category == "URGENT":
                # Still send urgent during quiet hours, but silent
                logger.debug("Quiet hours - sending urgent with silent notification")
                return True
            else:
                logger.debug(f"Quiet hours - skipping {category} notification")
                return False

        # Normal hours - send everything
        return True

    def get_notification_mode(self, category: str, dt: datetime = None) -> dict:
        """
        Get notification mode (sound, silent, etc.)

        Args:
            category: Email category
            dt: Datetime to check

        Returns:
            Dict with notification settings
        """
        if dt is None:
            dt = datetime.now()

        should_send = self.should_send_notification(category, dt)

        if not should_send:
            return {"send": False, "reason": "quiet_hours_or_weekend"}

        # Determine if should be silent
        is_quiet = self.is_quiet_hours(dt)
        is_weekend = self.is_weekend(dt)

        if category == "URGENT":
            if is_quiet:
                return {"send": True, "silent": True, "reason": "urgent_quiet_hours"}
            else:
                return {"send": True, "silent": False, "reason": "urgent_normal"}
        elif category == "IMPORTANT":
            if is_weekend and self.weekend_mode == "urgent_only":
                return {"send": False, "reason": "weekend_urgent_only"}
            return {"send": True, "silent": True, "reason": "important_silent"}
        else:
            return {"send": True, "silent": True, "reason": "normal_silent"}

    @classmethod
    def from_env(cls) -> "TimeUrgencyManager":
        """Create from environment variables"""
        import os

        quiet_start = int(os.getenv("QUIET_HOURS_START", "22"))
        quiet_end = int(os.getenv("QUIET_HOURS_END", "7"))
        weekend_mode = os.getenv("WEEKEND_MODE", "silent")

        return cls(
            quiet_hours_start=quiet_start,
            quiet_hours_end=quiet_end,
            weekend_mode=weekend_mode,
        )


# Convenience function
def should_notify(category: str) -> bool:
    """
    Quick check if should send notification

    Args:
        category: Email category

    Returns:
        True if should send
    """
    manager = TimeUrgencyManager.from_env()
    return manager.should_send_notification(category)


if __name__ == "__main__":
    # Test
    manager = TimeUrgencyManager()

    now = datetime.now()
    print(f"Current time: {now}")
    print(f"Is quiet hours: {manager.is_quiet_hours(now)}")
    print(f"Is weekend: {manager.is_weekend(now)}")

    for category in ["URGENT", "IMPORTANT", "NORMAL"]:
        should_send = manager.should_send_notification(category, now)
        mode = manager.get_notification_mode(category, now)
        print(f"{category}: send={should_send}, mode={mode}")
