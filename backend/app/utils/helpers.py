import logging
from datetime import datetime
from typing import Any, Dict

def setup_logging():
    """Configure logging for the application"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
        ]
    )

def format_datetime(dt: datetime) -> str:
    """Format datetime to string"""
    return dt.isoformat() if dt else None

def sanitize_user_data(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Remove sensitive information from user data"""
    if "password_hash" in user_data:
        del user_data["password_hash"]
    if "password_reset_token" in user_data:
        del user_data["password_reset_token"]
    return user_data