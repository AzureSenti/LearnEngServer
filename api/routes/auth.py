from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, or_

from core.db import get_session
from core.security import (
    create_access_token,
    generate_refresh_token_string,
    get_refresh_token_expiry,
    hash_password,
    verify_password,
)
from model.dto.auth import (
    AuthTokenResponse,
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    RegisterRequest,
    RegisterResponse,
)
from model.entity.account import Account
from model.entity.refresh_token import RefreshToken
from model.entity.user import User

router = APIRouter(prefix="/auth", tags=["Auth"])


# ---------------------------------------------------------------------------
# Register
# ---------------------------------------------------------------------------


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    request: RegisterRequest,
    session: Session = Depends(get_session),
):
    """Register a new user account.

    1. Check email uniqueness in ``accounts``.
    2. Create a ``User`` profile.
    3. Create an ``Account`` linked to the user.
    4. Issue access + refresh tokens.
    """
    # Check for existing email or account_name
    existing = session.exec(
        select(Account).where(
            or_(Account.email == request.email, Account.account_name == request.account_name)
        )
    ).first()
    if existing:
        if existing.email == request.email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Account name already registered",
            )

    # Create user profile
    user = User(full_name=request.full_name)
    session.add(user)
    session.flush()  # get user_id before creating account

    # Create account with hashed password
    account = Account(
        account_name=request.account_name,
        email=request.email,
        password_hash=hash_password(request.password),
        user_id=user.user_id,
    )
    session.add(account)
    session.flush()

    # Generate tokens
    access_token = create_access_token(subject=account.account_id)
    refresh_token_str = generate_refresh_token_string()

    # Persist refresh token
    refresh_token = RefreshToken(
        account_id=account.account_id,
        token=refresh_token_str,
        expires_at=get_refresh_token_expiry(),
    )
    session.add(refresh_token)
    session.commit()

    return RegisterResponse(
        user_id=str(user.user_id),
        email=account.email,
        full_name=user.full_name,
        account_name=account.account_name,
        tokens=AuthTokenResponse(
            access_token=access_token,
            refresh_token=refresh_token_str,
        ),
    )


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    session: Session = Depends(get_session),
):
    """Authenticate with email and password.

    1. Look up ``Account`` by email.
    2. Verify password.
    3. Fetch linked ``User`` profile.
    4. Issue access + refresh tokens.
    """

    # Find account by email or account_name
    account = session.exec(
        select(Account).where(
            or_(Account.email == request.identifier, Account.account_name == request.identifier)
        )
    ).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect identifier or password",
        )

    # Verify password
    if not verify_password(request.password, account.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect identifier or password",
        )

    # Fetch user profile
    user = session.get(User, account.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User profile not found",
        )

    # Generate tokens
    access_token = create_access_token(subject=account.account_id)
    refresh_token_str = generate_refresh_token_string()

    # Persist refresh token
    refresh_token = RefreshToken(
        account_id=account.account_id,
        token=refresh_token_str,
        expires_at=get_refresh_token_expiry(),
    )
    session.add(refresh_token)
    session.commit()

    return LoginResponse(
        user_id=str(user.user_id),
        full_name=user.full_name,
        avatar_url=user.avatar_url,
        email=account.email,
        account_name=account.account_name,
        coins=user.coins,
        current_streak=user.current_streak,
        longest_streak=user.longest_streak,
        tokens=AuthTokenResponse(
            access_token=access_token,
            refresh_token=refresh_token_str,
        ),
    )

# ---------------------------------------------------------------------------
# Refresh
# ---------------------------------------------------------------------------


@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh(
    request: RefreshTokenRequest,
    session: Session = Depends(get_session),
):
    """Exchange a valid refresh token for a new access token.

    The used refresh token is revoked after issuing the new access token.
    """
    # Look up refresh token
    token_record = session.exec(
        select(RefreshToken).where(RefreshToken.token == request.refresh_token)
    ).first()

    if not token_record:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    if token_record.is_revoked:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has been revoked",
        )

    if token_record.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has expired",
        )

    # Revoke the old refresh token
    token_record.is_revoked = True
    session.add(token_record)

    # Issue new access token
    access_token = create_access_token(subject=token_record.account_id)
    session.commit()

    return RefreshTokenResponse(access_token=access_token)


# ---------------------------------------------------------------------------
# Logout
# ---------------------------------------------------------------------------


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    request: RefreshTokenRequest,
    session: Session = Depends(get_session),
):
    """Revoke a refresh token (logout).

    Marks the refresh token as revoked so it can no longer be used.
    """
    token_record = session.exec(
        select(RefreshToken).where(RefreshToken.token == request.refresh_token)
    ).first()

    if token_record and not token_record.is_revoked:
        token_record.is_revoked = True
        session.add(token_record)
        session.commit()

    return {"message": "Logged out successfully"}