import uuid as _uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlmodel import Session

from core.db import get_session
from core.security import decode_access_token
from model.entity.account import Account
from model.entity.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
) -> User:
    """Decode the Bearer token and return the corresponding User profile.

    The access token ``sub`` claim contains the account_id (UUID).
    We look up the Account, then fetch the linked User.

    Raises:
        HTTPException 401: If the token is invalid/expired or user not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        account_id_str = decode_access_token(token)
        account_id = _uuid.UUID(account_id_str)
    except (JWTError, ValueError):
        raise credentials_exception

    account = session.get(Account, account_id)
    if account is None:
        raise credentials_exception

    user = session.get(User, account.user_id)
    if user is None:
        raise credentials_exception

    return user
