from pydantic import BaseModel, Field

class UpdateProfileRequest(BaseModel):
    full_name: str | None = Field(default=None, max_length=100)
    avatar_url: str | None = Field(default=None, max_length=500)

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=6, description="Minimum 6 characters")
