from fastapi import APIRouter, Depends, HTTPException

from model.dto.auth import LoginResponse, LoginRequest

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest
                ):
    return {

    }