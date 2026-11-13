import bcrypt

_ENCODING = "utf-8"


def make_hash(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(_ENCODING), bcrypt.gensalt()).decode(_ENCODING)


def check_password(plain: str, stored_hash: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode(_ENCODING), stored_hash.encode(_ENCODING))
    except ValueError:
        # Malformed hash in the database -> treat as a failed login, not a crash.
        return False
