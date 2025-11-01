from fastapi import APIRouter, HTTPException, status, Body
from backend.app.schemas.auth import (
    UserSignupRequest, UserLoginRequest, UserLoginResponse,
    PasswordResetRequest, OTPRequest, OTPResendRequest,
    MessageResponse, DeleteAccountRequest, ChangePasswordRequest
)
from backend.app.services.auth_service import auth_service

# Legacy routes for backward compatibility with frontend
router = APIRouter()

@router.post("/request-registration-otp", response_model=MessageResponse)
def request_registration_otp(user_data: UserSignupRequest):
    """Legacy endpoint: Register a new user (sends OTP for verification)"""
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

@router.post("/verify-registration-otp", response_model=UserLoginResponse)
def verify_registration_otp(otp_data: OTPRequest):
    """Legacy endpoint: Verify OTP and complete registration"""
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
def resend_otp_legacy(resend_data: OTPResendRequest):
    """Legacy endpoint: Resend OTP for email verification"""
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
def login_legacy(login_data: UserLoginRequest):
    """Legacy endpoint: Authenticate user and return access token"""
    try:
        return auth_service.login_user(login_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )

@router.post("/request-password-reset", response_model=MessageResponse)
def request_password_reset_legacy(reset_data: PasswordResetRequest):
    """Legacy endpoint: Request password reset (sends OTP)"""
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

@router.post("/verify-otp", response_model=MessageResponse)
def verify_otp_legacy(otp_data: OTPRequest):
    """Legacy endpoint: Verify OTP for password reset"""
    # This is for password reset OTP verification
    try:
        # For password reset, we don't return login response, just confirmation
        # The frontend will redirect to reset password form after OTP verification
        stored_otp = auth_service.otp_store.get(otp_data.email)
        if not stored_otp or stored_otp["purpose"] != "password_reset":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No password reset OTP found for this email"
            )
        
        from datetime import datetime
        if stored_otp["expires"] < datetime.utcnow():
            del auth_service.otp_store[otp_data.email]
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OTP has expired"
            )
        
        if stored_otp["otp"] != otp_data.otp:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid OTP"
            )
        
        # Don't delete OTP yet, keep it for password reset
        return MessageResponse(message="OTP verified successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OTP verification failed: {str(e)}"
        )

@router.post("/reset-password", response_model=MessageResponse)
def reset_password_legacy(
    email: str = Body(...),
    otp: str = Body(...),
    new_password: str = Body(...)
):
    """Legacy endpoint: Reset password using OTP"""
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

@router.post("/change-password", response_model=MessageResponse)
def change_password_legacy(change_request: ChangePasswordRequest):
    """Legacy endpoint: Change password while logged in"""
    try:
        # Import dependencies
        from backend.app.database.repositories import user_repository
        from backend.app.core.security import verify_password, hash_password
        
        # Get user from database
        user = user_repository.get_user_by_email(change_request.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or current password"
            )
        
        # Verify current password
        if not verify_password(change_request.current_password, user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or current password"
            )
        
        # Check if account is active
        user_status = user.get("status", "active")
        if user_status != "active":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is not active"
            )
        
        # Hash new password
        new_password_hash = hash_password(change_request.new_password)
        
        # Update password in database
        success = user_repository.update_user_password(user["_id"], new_password_hash)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update password. Please try again."
            )
        
        return MessageResponse(
            message="Password changed successfully",
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Password change failed: {str(e)}"
        )

@router.post("/delete-account", response_model=MessageResponse)
def delete_account_legacy(delete_request: DeleteAccountRequest):
    """Legacy endpoint: Delete user account"""
    try:
        # Validate confirmation text
        if delete_request.confirmation.lower() != "delete my account":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Please type exactly 'delete my account' to confirm deletion"
            )
        
        # Verify user credentials before deletion
        from backend.app.database.repositories import user_repository
        from backend.app.core.security import verify_password
        
        # Get user from database
        user = user_repository.get_user_by_email(delete_request.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify password
        if not verify_password(delete_request.password, user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Check if account is already deleted
        user_status = user.get("status", "active")
        if user_status == "deleted":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account is already deleted"
            )
        
        # Soft delete the user (set status to deleted)
        success = user_repository.delete_user(user["_id"])
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete account. Please try again."
            )
        
        return MessageResponse(
            message="Account deleted successfully. We're sorry to see you go!",
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Account deletion failed: {str(e)}"
        )

# TEMPORARY: Test endpoint to get OTP for development (REMOVE IN PRODUCTION!)
@router.get("/dev-get-otp/{email}")
def dev_get_otp(email: str):
    """DEVELOPMENT ONLY: Get OTP for testing purposes"""
    from backend.app.services.auth_service import auth_service
    otp_data = auth_service.otp_store.get(email)
    if otp_data:
        return {
            "email": email,
            "otp": otp_data["otp"], 
            "expires": str(otp_data["expires"]),
            "purpose": otp_data["purpose"]
        }
    return {"message": "No OTP found for this email"}