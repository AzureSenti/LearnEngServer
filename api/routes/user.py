from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from api.deps import get_current_user
from core.db import get_session
from core.security import hash_password, verify_password
from model.dto.user import UpdateProfileRequest, ChangePasswordRequest
from model.entity.account import Account
from model.entity.user import User

router = APIRouter(prefix="/user", tags=["User"])

@router.put("/profile")
async def update_profile(
    request: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Update user's personal information (full_name, avatar_url)."""
    if request.full_name is not None:
        current_user.full_name = request.full_name
    if request.avatar_url is not None:
        current_user.avatar_url = request.avatar_url
    
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    
    return {
        "user_id": str(current_user.user_id),
        "full_name": current_user.full_name,
        "avatar_url": current_user.avatar_url,
        "coins": current_user.coins,
        "current_streak": current_user.current_streak,
        "longest_streak": current_user.longest_streak,
    }

@router.put("/password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Change user's password."""
    account = session.exec(
        select(Account).where(Account.user_id == current_user.user_id)
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found",
        )
        
    if not verify_password(request.current_password, account.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password",
        )
        
    account.password_hash = hash_password(request.new_password)
    session.add(account)
    session.commit()
    
    return {"message": "Password updated successfully"}
