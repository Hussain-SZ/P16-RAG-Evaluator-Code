from fastapi import APIRouter, HTTPException, Depends, status, Body
from pymongo.mongo_client import MongoClient
from backend.app.models import User
from backend.app.auth import hash_password, verify_password, create_access_token, create_reset_token, verify_reset_token, get_current_user
from datetime import datetime, timedelta
from pydantic import BaseModel
from pymongo.server_api import ServerApi
from bson import ObjectId
import os
import random
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

uri = os.getenv("MONGO_URI")
if not uri:
    raise ValueError("MONGO_URI environment variable is not set!")

print(f"Connecting to MongoDB...")
router = APIRouter(prefix="/auth", tags=["Authentication"])

# MongoDB connection with SSL configuration
try:
    client = MongoClient(
        uri,server_api=ServerApi('1'))
    db = client["rag_evaluator"]
    users = db["users"]
    
    # Test MongoDB connection
    client.admin.command('ping')
    print("Successfully connected to MongoDB!")
    print(f"   Database: {db.name}")
    print(f"   Collections: {db.list_collection_names()}")
except Exception as e:
    print(f"MongoDB connection failed: {e}")
    # Create a dummy connection for development
    client = None
    db = None
    users = None

# OTP storage (in production, use Redis or database with expiration)
otp_store = {}
# Pending registrations storage (temporary user data until OTP verification)
pending_registrations = {}

# Function to generate 6-digit OTP
def generate_otp():
    return str(random.randint(100000, 999999))

# Function to send OTP via email using SendGrid API
def send_otp_email(email: str, otp: str, purpose: str = "password_reset") -> bool:
    """
    Send OTP to user email via SendGrid API (HTTPS, works on Render)
    """
    api_key = os.getenv("SENDGRID_API_KEY")
    from_email = os.getenv("SENDGRID_FROM_EMAIL", "noreply@ragevaluator.com")
    
    print(f"Attempting to send OTP to {email}")
    print(f"   Using SendGrid API")
    
    if not api_key:
        print("SENDGRID_API_KEY not set in environment variables")
        print(f"OTP for {email}: {otp}")  # Print for development
        return True  # Return True for development
    
    url = "https://api.sendgrid.com/v3/mail/send"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Create HTML email content based on purpose
    if purpose == "registration":
        subject = "Email Verification OTP - RAG Evaluator"
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h2 style="color: #667eea;">Welcome to RAG Evaluator!</h2>
                <p>Thank you for registering. Please verify your email address.</p>
                <p>Your verification code is:</p>
                <h1 style="color: #764ba2; font-size: 36px; letter-spacing: 5px;">{otp}</h1>
                <p>This code will expire in 10 minutes.</p>
                <p>If you didn't request this, please ignore this email.</p>
                <br>
                <p style="color: #666; font-size: 12px;">© 2025 RAG Pipeline Evaluator</p>
            </body>
        </html>
        """
    else:
        subject = "Password Reset OTP - RAG Evaluator"
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h2 style="color: #667eea;">Password Reset Request</h2>
                <p>You have requested to reset your password.</p>
                <p>Your OTP code is:</p>
                <h1 style="color: #764ba2; font-size: 36px; letter-spacing: 5px;">{otp}</h1>
                <p>This code will expire in 10 minutes.</p>
                <p>If you didn't request this, please ignore this email.</p>
                <br>
                <p style="color: #666; font-size: 12px;">© 2025 RAG Pipeline Evaluator</p>
            </body>
        </html>
        """
    
    payload = {
        "personalizations": [{"to": [{"email": email}]}],
        "from": {"email": from_email},
        "subject": subject,
        "content": [
            {"type": "text/plain", "value": f"Your OTP is {otp}. This code will expire in 10 minutes."},
            {"type": "text/html", "value": html_content}
        ]
    }
    
    try:
        print("   Sending request to SendGrid API...")
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        
        if response.status_code == 202:
            print(f"OTP sent to {email} via SendGrid")
            print(f"OTP for {email}: {otp}")  # Still print for development/debugging
            return True
        else:
            print(f"SendGrid API failed ({response.status_code}): {response.text}")
            print(f"OTP for {email}: {otp}")  # Print for development
            return True  # Return True for development even if email fails
    except requests.exceptions.Timeout:
        print(f"SendGrid API request timed out")
        print(f"OTP for {email}: {otp}")  # Print for development
        return True  # Return True for development
    except Exception as e:
        print(f"Error sending OTP via SendGrid: {e}")
        print(f"OTP for {email}: {otp}")  # Print for development
        return True  # Return True for development

# -------- UC-001 Registration with OTP
@router.post("/request-registration-otp")
def request_registration_otp(user: User):
    """Send OTP to user's email for registration verification"""
    print(f"Registration OTP request for: {user.email}")
    
    # Check if email already exists
    if users.find_one({"email": user.email}):
        print(f"Email already registered: {user.email}")
        raise HTTPException(status_code=400, detail="Email already registered")
    
    print(f"Email available: {user.email}")
    
    # Generate OTP
    otp = generate_otp()
    print(f"Generated OTP: {otp}")
    
    # Store user data temporarily with OTP
    pending_registrations[user.email] = {
        "user_data": user.dict(),
        "otp": otp,
        "expires_at": datetime.utcnow() + timedelta(minutes=10)
    }
    print(f"Registration data stored for {user.email}")
    
    # Send OTP via email
    print(f"Attempting to send registration OTP email...")
    if send_otp_email(user.email, otp, purpose="registration"):
        print(f"Registration OTP sent successfully")
        # Print OTP to console for development
        print(f"\n{'='*50}")
        print(f"REGISTRATION OTP for {user.email}")
        print(f"{'='*50}")
        print(f"   OTP CODE: {otp}")
        print(f"   Expires: {pending_registrations[user.email]['expires_at']}")
        print(f"{'='*50}\n")
        return {"message": "OTP has been sent to your email"}
    else:
        print(f"Email sending failed")
        raise HTTPException(status_code=500, detail="Failed to send OTP")

@router.post("/verify-registration-otp")
def verify_registration_otp(email: str = Body(...), otp: str = Body(...)):
    """Verify OTP and create user account"""
    print(f"Verifying registration OTP for: {email}")
    
    if email not in pending_registrations:
        print(f"No pending registration found for: {email}")
        raise HTTPException(status_code=400, detail="No registration request found for this email")
    
    stored_data = pending_registrations[email]
    
    # Check if OTP expired
    if datetime.utcnow() > stored_data["expires_at"]:
        del pending_registrations[email]
        print(f"OTP expired for: {email}")
        raise HTTPException(status_code=400, detail="OTP has expired. Please request a new one.")
    
    # Verify OTP
    if stored_data["otp"] != otp:
        print(f"Invalid OTP for: {email}")
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    print(f"OTP verified for: {email}")
    
    # Create user account
    user_data = stored_data["user_data"]
    hashed = hash_password(user_data["password_hash"])
    new_user = user_data.copy()
    new_user["password_hash"] = hashed
    
    try:
        users.insert_one(new_user)
        print(f"User account created: {email}")
    except Exception as e:
        print(f"Failed to create user: {e}")
        raise HTTPException(status_code=500, detail="Failed to create user account")
    
    # Clear pending registration
    del pending_registrations[email]
    
    return {"message": "Account created successfully! You can now log in."}

@router.post("/register")
def register_user(user: User):
    """Legacy registration endpoint - redirects to OTP flow"""
    raise HTTPException(
        status_code=400, 
        detail="Please use /request-registration-otp endpoint for registration"
    )


# -------- UC-002 Login
class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/login")
def login_user(request: LoginRequest):
    print(f"Login attempt for email: {request.email}")
    user = users.find_one({"email": request.email})
    if not user or not verify_password(request.password, user["password_hash"]):
        print(f"Login failed for email: {request.email}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token_data = {"sub": str(user["_id"]), "role": user["role"]}
    access_token = create_access_token(token_data, expires_delta=timedelta(hours=1))
    return {"message": "Login Successful", "access_token": access_token, "token_type": "bearer"}


# -------- UC-003 Password Reset with OTP
@router.post("/request-password-reset")
def request_password_reset(email: str = Body(..., embed=True)):
    """Send OTP to user's email for password reset"""
    print(f"Password reset request for: {email}")
    
    # Check if user exists
    user = users.find_one({"email": email})
    if not user:
        print(f"User not found: {email}")
        raise HTTPException(status_code=404, detail="User not found")
    
    print(f"User found: {email}")
    
    # Generate OTP
    otp = generate_otp()
    print(f"Generated OTP: {otp}")
    
    # Store OTP with expiration (10 minutes)
    otp_store[email] = {
        "otp": otp,
        "expires_at": datetime.utcnow() + timedelta(minutes=10)
    }
    print(f"OTP stored for {email}")
    
    # Send OTP via email
    print(f"Attempting to send OTP email...")
    if send_otp_email(email, otp):
        print(f"Request completed successfully")
        return {"message": "OTP has been sent to your email"}
    else:
        print(f"Email sending failed")
        raise HTTPException(status_code=500, detail="Failed to send OTP")

@router.post("/verify-otp")
def verify_otp(email: str = Body(...), otp: str = Body(...)):
    """Verify OTP and return a reset token"""
    if email not in otp_store:
        raise HTTPException(status_code=400, detail="No OTP request found for this email")
    
    stored_data = otp_store[email]
    
    # Check if OTP expired
    if datetime.utcnow() > stored_data["expires_at"]:
        del otp_store[email]
        raise HTTPException(status_code=400, detail="OTP has expired")
    
    # Verify OTP
    if stored_data["otp"] != otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    # OTP is valid, generate reset token
    reset_token = create_reset_token(email)
    
    # Clear OTP from store
    del otp_store[email]
    
    return {"message": "OTP verified successfully", "reset_token": reset_token}

@router.post("/reset-password")
def reset_password(token: str = Body(...), new_password: str = Body(...)):
    email = verify_reset_token(token)
    user = users.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    hashed = hash_password(new_password)
    users.update_one({"email": email}, {"$set": {"password_hash": hashed, "updated_at": datetime.utcnow()}})
    return {"message": "Password has been successfully reset"}


# -------- UC-004 Delete User
@router.delete("/delete-account")
def delete_user_account(current_user: dict = Depends(get_current_user)):
    """Delete the currently authenticated user's account"""
    user_id = current_user.get("user_id")
    
    # Find and delete the user
    result = users.delete_one({"_id": ObjectId(user_id)})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": "Account deleted successfully"}


@router.delete("/delete-user/{user_id}")
def delete_user_by_id(user_id: str, current_user: dict = Depends(get_current_user)):
    """Admin endpoint to delete any user by ID"""
    # Check if current user is admin (from token data)
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    
    # Delete the specified user
    result = users.delete_one({"_id": ObjectId(user_id)})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": f"User {user_id} deleted successfully"}