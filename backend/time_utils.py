from datetime import datetime, timezone


# Database DateTime columns store naive UTC timestamps.
def utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)
