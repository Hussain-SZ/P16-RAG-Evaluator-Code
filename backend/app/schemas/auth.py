from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserSignupRequest(BaseModel):
    """Schema for user signup request"""
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)

class UserLoginRequest(BaseModel):
    """Schema for user login request"""
    email: EmailStr
    password: str

class UserLoginResponse(BaseModel):
    """Schema for user login response"""
    access_token: str
    token_type: str = "bearer"
    user_id: str
    name: str
    email: str
    role: str

class UserProfile(BaseModel):
    """Schema for user profile response"""
    user_id: str
    name: str
    email: str
    role: str
    status: str
    created_at: str
    last_login: Optional[str] = None

class PasswordResetRequest(BaseModel):
    """Schema for password reset request"""
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation"""
    token: str
    new_password: str = Field(..., min_length=6, max_length=100)

class OTPRequest(BaseModel):
    """Schema for OTP verification request"""
    email: EmailStr
    otp: str = Field(..., min_length=6, max_length=6)

class OTPResendRequest(BaseModel):
    """Schema for OTP resend request"""
    email: EmailStr

class MessageResponse(BaseModel):
    """Generic message response schema"""
    message: str
    success: bool = True

class ChangePasswordRequest(BaseModel):
    """Schema for changing password while logged in"""
    email: EmailStr
    current_password: str = Field(..., min_length=1, max_length=100)
    new_password: str = Field(..., min_length=6, max_length=100)

class DeleteAccountRequest(BaseModel):
    """Schema for account deletion request"""
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)
    confirmation: str = Field(..., description="Must be exactly 'delete my account'")

class ErrorResponse(BaseModel):
    """Error response schema"""
    detail: str
    success: bool = False