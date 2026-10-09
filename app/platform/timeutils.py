from datetime import datetime, timezone


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def as_aware_utc(value: datetime) -> datetime:
    """Treat a naive datetime as UTC instead of raising on comparison.

    Postgres (the real target database) always returns timezone-aware
    values for TIMESTAMP WITH TIME ZONE columns. SQLite — used only in
    tests, since there's no local Postgres/Docker in this environment —
    silently drops tzinfo on read even though the value was written as
    UTC. Without this, comparing a freshly-read row's expiry against
    datetime.now(timezone.utc) raises TypeError under SQLite while working
    fine under Postgres.
    """
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value
