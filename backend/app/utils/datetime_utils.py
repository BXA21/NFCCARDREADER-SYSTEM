"""
Datetime utility functions for consistent date/time handling.
"""

from datetime import datetime, date, time, timedelta
from typing import Optional


def utcnow() -> datetime:
    """
    Get current UTC datetime.
    
    Returns:
        Current datetime in UTC
    """
    return datetime.utcnow()


def today() -> date:
    """
    Get current date in UTC.
    
    Returns:
        Current date
    """
    return datetime.utcnow().date()


def format_datetime(dt: datetime, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format a datetime object to string.
    
    Args:
        dt: Datetime object
        fmt: Format string (default: YYYY-MM-DD HH:MM:SS)
        
    Returns:
        Formatted datetime string
    """
    return dt.strftime(fmt)


def format_date(d: date, fmt: str = "%Y-%m-%d") -> str:
    """
    Format a date object to string.
    
    Args:
        d: Date object
        fmt: Format string (default: YYYY-MM-DD)
        
    Returns:
        Formatted date string
    """
    return d.strftime(fmt)


def parse_datetime(dt_str: str, fmt: str = "%Y-%m-%d %H:%M:%S") -> Optional[datetime]:
    """
    Parse a string to datetime object.
    
    Args:
        dt_str: Datetime string
        fmt: Format string
        
    Returns:
        Datetime object or None if parsing fails
    """
    try:
        return datetime.strptime(dt_str, fmt)
    except ValueError:
        return None


def is_same_day(dt1: datetime, dt2: datetime) -> bool:
    """
    Check if two datetimes are on the same day.
    
    Args:
        dt1: First datetime
        dt2: Second datetime
        
    Returns:
        True if same day, False otherwise
    """
    return dt1.date() == dt2.date()


def get_time_difference_seconds(dt1: datetime, dt2: datetime) -> int:
    """
    Get the difference between two datetimes in seconds.
    Handles both timezone-aware and timezone-naive datetimes.
    
    Args:
        dt1: First datetime
        dt2: Second datetime
        
    Returns:
        Absolute difference in seconds
    """
    # Convert both to UTC if timezone-aware, or strip timezone if mixed
    if dt1.tzinfo is not None and dt2.tzinfo is None:
        # dt1 has timezone, dt2 doesn't - remove timezone from dt1
        dt1 = dt1.replace(tzinfo=None)
    elif dt1.tzinfo is None and dt2.tzinfo is not None:
        # dt2 has timezone, dt1 doesn't - remove timezone from dt2
        dt2 = dt2.replace(tzinfo=None)
    elif dt1.tzinfo is not None and dt2.tzinfo is not None:
        # Both have timezones - convert to UTC
        import pytz
        dt1 = dt1.astimezone(pytz.UTC).replace(tzinfo=None)
        dt2 = dt2.astimezone(pytz.UTC).replace(tzinfo=None)
    
    return abs(int((dt1 - dt2).total_seconds()))

