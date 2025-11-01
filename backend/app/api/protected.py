from fastapi import APIRouter, Depends
from backend.app.core.security import get_current_user
from backend.app.schemas.auth import UserProfile, MessageResponse

router = APIRouter()

@router.get("/me", response_model=dict)
async def read_user_data(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return {
        "message": "Access granted!",
        "user": current_user
    }

@router.get("/dashboard")
async def dashboard(current_user: dict = Depends(get_current_user)):
    """Protected dashboard endpoint"""
    return {
        "message": f"Welcome to dashboard, user {current_user['user_id']}",
        "data": "This is protected content"
    }