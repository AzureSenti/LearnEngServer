import secrets
import uuid as _uuid
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt

from core.config import settings

# ---------------------------------------------------------------------------
# Password hashing (bcrypt)
# ---------------------------------------------------------------------------


def hash_password(plain_password: str) -> str:
    """Hash a plain-text password using bcrypt."""
    password_bytes = plain_password.encode("utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against its bcrypt hash."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


# ---------------------------------------------------------------------------
# JWT access token
# ---------------------------------------------------------------------------

ALGORITHM = "HS256"


def create_access_token(
    subject: _uuid.UUID | str,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a signed JWT access token.

    Args:
        subject: Value stored in the ``sub`` claim (typically account_id).
        expires_delta: Custom expiry duration. Falls back to the configured
            ``ACCESS_TOKEN_EXPIRE_MINUTES`` from settings.

    Returns:
        Encoded JWT string.
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    expire = datetime.now(timezone.utc) + expires_delta
    payload = {"sub": str(subject), "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> str:
    """Decode and validate a JWT access token.

    Args:
        token: The encoded JWT string.

    Returns:
        The ``sub`` claim value (account_id as string).

    Raises:
        JWTError: If the token is invalid or expired.
    """
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    sub: str | None = payload.get("sub")
    if sub is None:
        raise JWTError("Token missing 'sub' claim")
    return sub


# ---------------------------------------------------------------------------
# Refresh token
# ---------------------------------------------------------------------------


def generate_refresh_token_string() -> str:
    """Generate a cryptographically secure random refresh token string."""
    return secrets.token_urlsafe(64)


def get_refresh_token_expiry() -> datetime:
    """Return the expiry datetime for a new refresh token."""
    return datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS,
    )
