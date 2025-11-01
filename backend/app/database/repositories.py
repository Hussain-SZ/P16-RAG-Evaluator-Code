from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId
from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError
from backend.app.models.user import User
from backend.app.database.connection import get_users_collection

class UserRepository:
    """Repository class for user database operations"""
    
    def __init__(self):
        self._collection: Optional[Collection] = None
    
    @property
    def collection(self) -> Collection:
        """Lazy loading of collection"""
        if self._collection is None:
            self._collection = get_users_collection()
        return self._collection
    
    def create_user(self, user_data: Dict[str, Any]) -> Optional[str]:
        """Create a new user and return the user ID"""
        try:
            user_data["created_at"] = datetime.utcnow()
            result = self.collection.insert_one(user_data)
            return str(result.inserted_id)
        except DuplicateKeyError:
            raise ValueError("User with this email already exists")
        except Exception as e:
            raise RuntimeError(f"Failed to create user: {str(e)}")
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        try:
            user = self.collection.find_one({"_id": ObjectId(user_id)})
            if user:
                user["_id"] = str(user["_id"])
            return user
        except Exception as e:
            raise RuntimeError(f"Failed to get user by ID: {str(e)}")
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        try:
            user = self.collection.find_one({"email": email})
            if user:
                user["_id"] = str(user["_id"])
            return user
        except Exception as e:
            raise RuntimeError(f"Failed to get user by email: {str(e)}")
    
    def update_user(self, user_id: str, update_data: Dict[str, Any]) -> bool:
        """Update user data"""
        try:
            update_data["updated_at"] = datetime.utcnow()
            result = self.collection.update_one(
                {"_id": ObjectId(user_id)}, 
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            raise RuntimeError(f"Failed to update user: {str(e)}")
    
    def update_last_login(self, user_id: str) -> bool:
        """Update user's last login timestamp"""
        return self.update_user(user_id, {"last_login": datetime.utcnow()})
    
    def set_password_reset_token(self, email: str, token: str, expires_at: datetime) -> bool:
        """Set password reset token for user"""
        try:
            result = self.collection.update_one(
                {"email": email},
                {
                    "$set": {
                        "password_reset_token": token,
                        "password_reset_expires": expires_at,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            raise RuntimeError(f"Failed to set password reset token: {str(e)}")
    
    def clear_password_reset_token(self, email: str) -> bool:
        """Clear password reset token"""
        try:
            result = self.collection.update_one(
                {"email": email},
                {
                    "$unset": {
                        "password_reset_token": "",
                        "password_reset_expires": ""
                    },
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            return result.modified_count > 0
        except Exception as e:
            raise RuntimeError(f"Failed to clear password reset token: {str(e)}")
    
    def update_password(self, email: str, new_password_hash: str) -> bool:
        """Update user password by email"""
        return self.update_user_by_email(
            email, 
            {"password_hash": new_password_hash}
        )
    
    def update_user_password(self, user_id: str, new_password_hash: str) -> bool:
        """Update user password by ID"""
        return self.update_user(
            user_id, 
            {"password_hash": new_password_hash}
        )
    
    def update_user_by_email(self, email: str, update_data: Dict[str, Any]) -> bool:
        """Update user by email"""
        try:
            update_data["updated_at"] = datetime.utcnow()
            result = self.collection.update_one(
                {"email": email}, 
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            raise RuntimeError(f"Failed to update user by email: {str(e)}")
    
    def delete_user(self, user_id: str) -> bool:
        """Soft delete user (set status to deleted)"""
        return self.update_user(
            user_id, 
            {"status": "deleted", "updated_at": datetime.utcnow()}
        )
    
    def get_all_users(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all users with pagination"""
        try:
            cursor = self.collection.find(
                {"status": {"$ne": "deleted"}},
                {"password_hash": 0}  # Exclude password hash
            ).skip(offset).limit(limit)
            
            users = []
            for user in cursor:
                user["_id"] = str(user["_id"])
                users.append(user)
            return users
        except Exception as e:
            raise RuntimeError(f"Failed to get users: {str(e)}")

# Global repository instance will be created lazily
_user_repository = None

def get_user_repository() -> UserRepository:
    """Get or create user repository instance"""
    global _user_repository
    if _user_repository is None:
        _user_repository = UserRepository()
    return _user_repository

# For backward compatibility, create a lazy-loaded instance
class LazyUserRepository:
    def __getattr__(self, name):
        return getattr(get_user_repository(), name)

user_repository = LazyUserRepository()