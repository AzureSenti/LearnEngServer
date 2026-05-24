from pydantic import BaseModel

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    userId: int
    fullName: str
    avatarUrl: str
    email: str
    coins: int
    token: str
