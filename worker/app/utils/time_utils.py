from datetime import datetime, timezone, timedelta

def get_now():
    """Get current time in GMT+7 (Asia/Bangkok)."""
    # We use a fixed offset to ensure it's always GMT+7 regardless of system settings
    return datetime.now(timezone(timedelta(hours=7)))
