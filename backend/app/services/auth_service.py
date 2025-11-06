import random
import requests
from typing import Dict, Optional
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from backend.app.core.security import (
    hash_password, verify_password, create_access_token, 
    create_reset_token, verify_reset_token
)
from backend.app.database.repositories import user_repository
from backend.app.schemas.auth import (
    UserSignupRequest, UserLoginRequest, UserLoginResponse, 
    PasswordResetRequest, PasswordResetConfirm
)
from backend.app.config.settings import settings

class AuthService:
    """Service class for authentication operations"""
    
    def __init__(self):
        self.otp_store: Dict[str, Dict] = {}  # In production, use Redis
        self.pending_registrations: Dict[str, Dict] = {}  # In production, use Redis
    
    def generate_otp(self) -> str:
        """Generate 6-digit OTP"""
        return str(random.randint(100000, 999999))
    
    def send_otp_email(self, email: str, otp: str, purpose: str = "verification") -> bool:
        """Send OTP via email using SendGrid"""
        if not settings.sendgrid_api_key:
            print("SENDGRID_API_KEY not set in environment variables")
            return False
        
        try:
            url = "https://api.sendgrid.com/v3/mail/send"
            headers = {
                "Authorization": f"Bearer {settings.sendgrid_api_key}",
                "Content-Type": "application/json"
            }
            
            subject = "Email Verification" if purpose == "verification" else "Password Reset"
            content = f"Your OTP is: {otp}. Valid for 10 minutes."
            
            data = {
                "personalizations": [{
                    "to": [{"email": email}],
                    "subject": subject
                }],
                "from": {"email": settings.sendgrid_from_email},
                "content": [{
                    "type": "text/plain",
                    "value": content
                }]
            }
            
            response = requests.post(url, json=data, headers=headers)
            return response.status_code == 202
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False
    
    def register_user(self, user_data: UserSignupRequest) -> Dict[str, str]:
        """Register a new user (step 1: send OTP)"""
        # Check if user already exists
        existing_user = user_repository.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Generate OTP and store pending registration
        otp = self.generate_otp()
        otp_expiry = datetime.utcnow() + timedelta(minutes=10)
        
        self.otp_store[user_data.email] = {
            "otp": otp,
            "expires": otp_expiry,
            "purpose": "registration"
        }
        
        # Store pending user data
        self.pending_registrations[user_data.email] = {
            "name": user_data.name,
            "email": user_data.email,
            "password_hash": hash_password(user_data.password),
            "role": "developer",  # Default role
            "status": "active",   # Default status
            "is_email_verified": True,  # Set to True after OTP verification
            "created_at": datetime.utcnow()
        }
        
        # Send OTP email
        email_sent = self.send_otp_email(user_data.email, otp, "verification")
        
        return {
            "message": "OTP sent to email for verification",
            "email_sent": str(email_sent)
        }
    
    def verify_otp_and_complete_registration(self, email: str, otp: str) -> UserLoginResponse:
        """Verify OTP and complete user registration"""
        # Check OTP
        stored_otp = self.otp_store.get(email)
        if not stored_otp:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No OTP found for this email"
            )
        
        if stored_otp["expires"] < datetime.utcnow():
            del self.otp_store[email]
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OTP has expired"
            )
        
        if stored_otp["otp"] != otp:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid OTP"
            )
        
        # Get pending registration data
        pending_user = self.pending_registrations.get(email)
        if not pending_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No pending registration found"
            )
        
        # Create user in database
        user_id = user_repository.create_user(pending_user)
        
        # Clean up temporary storage
        del self.otp_store[email]
        del self.pending_registrations[email]
        
        # Create access token with user ID and email
        access_token = create_access_token(data={"sub": user_id, "email": email})
        
        return UserLoginResponse(
            access_token=access_token,
            token_type="bearer",
            user_id=user_id,
            name=pending_user["name"],
            email=pending_user["email"],
            role="developer"
        )
    
    def login_user(self, login_data: UserLoginRequest) -> UserLoginResponse:
        """Authenticate user and return access token"""
        # Get user from database
        user = user_repository.get_user_by_email(login_data.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify password
        if not verify_password(login_data.password, user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Check user status (with default for backward compatibility)
        user_status = user.get("status", "active")  # Default to "active" if not set
        if user_status != "active":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is not active"
            )
        
        # Update last login
        user_repository.update_last_login(user["_id"])
        
        # Create access token with user ID and email
        access_token = create_access_token(data={"sub": user["_id"], "email": user["email"]})
        
        return UserLoginResponse(
            access_token=access_token,
            token_type="bearer",
            user_id=user["_id"],
            name=user["name"],
            email=user["email"],
            role=user.get("role", "developer")  # Default to "developer" if not set
        )
    
    def request_password_reset(self, reset_data: PasswordResetRequest) -> Dict[str, str]:
        """Send password reset OTP"""
        # Check if user exists
        user = user_repository.get_user_by_email(reset_data.email)
        if not user:
            # Don't reveal if user exists or not
            return {"message": "If the email exists, a reset OTP has been sent"}
        
        # Generate OTP
        otp = self.generate_otp()
        otp_expiry = datetime.utcnow() + timedelta(minutes=10)
        
        self.otp_store[reset_data.email] = {
            "otp": otp,
            "expires": otp_expiry,
            "purpose": "password_reset"
        }
        
        # Send OTP email
        self.send_otp_email(reset_data.email, otp, "password_reset")
        
        return {"message": "If the email exists, a reset OTP has been sent"}
    
    def reset_password_with_otp(self, email: str, otp: str, new_password: str) -> Dict[str, str]:
        """Reset password using OTP"""
        # Check OTP
        stored_otp = self.otp_store.get(email)
        if not stored_otp or stored_otp["purpose"] != "password_reset":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No password reset OTP found for this email"
            )
        
        if stored_otp["expires"] < datetime.utcnow():
            del self.otp_store[email]
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OTP has expired"
            )
        
        if stored_otp["otp"] != otp:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid OTP"
            )
        
        # Update password
        new_password_hash = hash_password(new_password)
        success = user_repository.update_password(email, new_password_hash)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update password"
            )
        
        # Clean up OTP
        del self.otp_store[email]
        
        return {"message": "Password reset successfully"}
    
    def resend_otp(self, email: str) -> Dict[str, str]:
        """Resend OTP for email verification"""
        # Check if there's a pending registration or password reset
        if email not in self.pending_registrations and email not in self.otp_store:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No pending operation found for this email"
            )
        
        # Generate new OTP
        otp = self.generate_otp()
        otp_expiry = datetime.utcnow() + timedelta(minutes=10)
        
        # Determine purpose
        purpose = "verification" if email in self.pending_registrations else "password_reset"
        
        self.otp_store[email] = {
            "otp": otp,
            "expires": otp_expiry,
            "purpose": purpose
        }
        
        # Send OTP email
        self.send_otp_email(email, otp, purpose)
        
        return {"message": "New OTP sent to email"}

# Create global service instance
auth_service = AuthService()