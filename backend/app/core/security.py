from datetime import datetime, timedelta
from jose import JWTError, jwt
import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from bson import ObjectId
from backend.app.config.settings import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

class SecurityManager:
    """Handles all authentication and security operations"""
    
    def __init__(self):
        self.secret_key = settings.jwt_secret
        self.algorithm = settings.jwt_algorithm
        self.access_token_expire_minutes = settings.access_token_expire_minutes
        self.reset_token_expire_minutes = settings.reset_token_expire_minutes
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt with proper byte encoding"""
        # Convert password to bytes and limit to 72 bytes for bcrypt
        password_bytes = password.encode('utf-8')[:72]
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against a bcrypt hash"""
        try:
            # Convert to bytes and limit to 72 bytes
            password_bytes = plain_password.encode('utf-8')[:72]
            hashed_bytes = hashed_password.encode('utf-8')
            return bcrypt.checkpw(password_bytes, hashed_bytes)
        except Exception as e:
            print(f"Password verification error: {e}")
            return False

    def create_access_token(self, data: dict, expires_delta: timedelta = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def decode_access_token(self, token: str) -> dict:
        """Decode and validate JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid token"
            )
    
    def create_reset_token(self, email: str) -> str:
        """Create short-lived password reset token"""
        expire = datetime.utcnow() + timedelta(minutes=self.reset_token_expire_minutes)
        data = {"sub": email, "exp": expire, "type": "reset"}
        return jwt.encode(data, self.secret_key, algorithm=self.algorithm)

    def verify_reset_token(self, token: str) -> str:
        """Verify password reset token and return email"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            if payload.get("type") != "reset":
                raise JWTError("Invalid token type")
            return payload["sub"]  # email
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Invalid or expired reset token"
            )

    def get_current_user(self, token: str = Depends(oauth2_scheme)) -> dict:
        """Extract current user from JWT token"""
        payload = self.decode_access_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid token payload"
            )
        return {"user_id": user_id}

# Create global security manager instance
security_manager = SecurityManager()

# Export commonly used functions
hash_password = security_manager.hash_password
verify_password = security_manager.verify_password
create_access_token = security_manager.create_access_token
decode_access_token = security_manager.decode_access_token
create_reset_token = security_manager.create_reset_token
verify_reset_token = security_manager.verify_reset_token
get_current_user = security_manager.get_current_user