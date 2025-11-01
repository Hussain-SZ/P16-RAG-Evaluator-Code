from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr
from bson import ObjectId

class PyObjectId(ObjectId):
    """Custom class for Pydantic to validate MongoDB ObjectId's in schemas"""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        json_schema = handler(core_schema)
        json_schema.update(type="string")
        return json_schema

class User(BaseModel):
    """User model for MongoDB documents"""
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr = Field(..., description="User's email address")
    password_hash: str = Field(..., description="Hashed password")
    role: str = Field(default="developer", description="User role: developer | admin")
    status: str = Field(
        default="active", 
        description="User status: active | inactive | suspended | deleted"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    last_login: Optional[datetime] = Field(default=None)
    
    # Email verification fields
    is_email_verified: bool = Field(default=False)
    email_verification_token: Optional[str] = Field(default=None)
    
    # Password reset fields
    password_reset_token: Optional[str] = Field(default=None)
    password_reset_expires: Optional[datetime] = Field(default=None)

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        populate_by_name = True