from datetime import datetime, timezone


def now_utc() -> datetime:
    """Timezone-aware 'now'. Every timestamp we persist goes through here."""
    return datetime.now(timezone.utc)
