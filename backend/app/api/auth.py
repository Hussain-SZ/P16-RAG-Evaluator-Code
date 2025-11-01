from fastapi import APIRouter, HTTPException, status, Body
from backend.app.schemas.auth import (
    UserSignupRequest, UserLoginRequest, UserLoginResponse,
    PasswordResetRequest, OTPRequest, OTPResendRequest,
    MessageResponse
)
from backend.app.services.auth_service import auth_service

router = APIRouter()

@router.post("/register", response_model=MessageResponse)
def register(user_data: UserSignupRequest):
    """Register a new user (sends OTP for verification)"""
    try:
        result = auth_service.register_user(user_data)
        return MessageResponse(message=result["message"])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@router.post("/verify-otp", response_model=UserLoginResponse)
def verify_otp(otp_data: OTPRequest):
    """Verify OTP and complete registration"""
    try:
        return auth_service.verify_otp_and_complete_registration(
            otp_data.email, otp_data.otp
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OTP verification failed: {str(e)}"
        )

@router.post("/resend-otp", response_model=MessageResponse)
def resend_otp(resend_data: OTPResendRequest):
    """Resend OTP for email verification"""
    try:
        result = auth_service.resend_otp(resend_data.email)
        return MessageResponse(message=result["message"])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Resend OTP failed: {str(e)}"
        )

@router.post("/login", response_model=UserLoginResponse)
def login(login_data: UserLoginRequest):
    """Authenticate user and return access token"""
    try:
        return auth_service.login_user(login_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )

@router.post("/forgot-password", response_model=MessageResponse)
def forgot_password(reset_data: PasswordResetRequest):
    """Request password reset (sends OTP)"""
    try:
        result = auth_service.request_password_reset(reset_data)
        return MessageResponse(message=result["message"])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Password reset request failed: {str(e)}"
        )

@router.post("/reset-password", response_model=MessageResponse)
def reset_password(
    email: str = Body(...),
    otp: str = Body(...),
    new_password: str = Body(...)
):
    """Reset password using OTP"""
    try:
        result = auth_service.reset_password_with_otp(email, otp, new_password)
        return MessageResponse(message=result["message"])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Password reset failed: {str(e)}"
        )