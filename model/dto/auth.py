from pydantic import BaseModel, EmailStr, Field


# ---------------------------------------------------------------------------
# Shared token response
# ---------------------------------------------------------------------------

class AuthTokenResponse(BaseModel):
    """Token pair returned on successful authentication."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


# ---------------------------------------------------------------------------
# Register
# ---------------------------------------------------------------------------

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, description="Minimum 6 characters")
    full_name: str = Field(min_length=1, max_length=100)
    account_name: str = Field(
        min_length=1,
        max_length=255,
        pattern=r"^[a-z0-9_]+$",
        description="Only lowercase letters, numbers, and underscores are allowed"
    )


class RegisterResponse(BaseModel):
    user_id: str
    email: str
    full_name: str
    account_name: str
    tokens: AuthTokenResponse


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------

class LoginRequest(BaseModel):
    identifier: str = Field(description="Email or account name")
    password: str


class LoginResponse(BaseModel):
    user_id: str
    full_name: str
    avatar_url: str
    email: str
    account_name: str
    coins: int
    current_streak: int
    longest_streak: int
    tokens: AuthTokenResponse


# ---------------------------------------------------------------------------
# Refresh / Logout
# ---------------------------------------------------------------------------

class RefreshTokenRequest(BaseModel):
    refresh_token: str


class RefreshTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
