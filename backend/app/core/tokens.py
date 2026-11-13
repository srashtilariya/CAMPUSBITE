"""Issuing and reading the bearer tokens handed out at login."""
from datetime import timedelta

from jose import JWTError, jwt

from app.core.clock import now_utc
from app.core.settings import load_config


def issue_token(account_id: int, role: str) -> str:
    cfg = load_config()
    claims = {
        "sub": str(account_id),
        "role": role,
        "exp": now_utc() + timedelta(minutes=cfg.token_ttl_minutes),
    }
    return jwt.encode(claims, cfg.token_secret, algorithm=cfg.token_algorithm)


def read_token(token: str) -> dict | None:
    cfg = load_config()
    try:
        return jwt.decode(token, cfg.token_secret, algorithms=[cfg.token_algorithm])
    except JWTError:
        return None
