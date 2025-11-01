from pymongo import MongoClient
from pymongo.server_api import ServerApi
from pymongo.database import Database
from pymongo.collection import Collection
from backend.app.config.settings import settings
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages MongoDB connection and provides database operations"""
    
    def __init__(self):
        self.client: MongoClient = None
        self.db: Database = None
        self.users_collection: Collection = None
        self._connected = False
    
    def connect(self):
        """Establish connection to MongoDB"""
        try:
            self.client = MongoClient(
                settings.mongo_uri,
                server_api=ServerApi('1')
            )
            
            # Test the connection
            self.client.admin.command('ping')
            
            # Get database and collections
            self.db = self.client[settings.database_name]
            self.users_collection = self.db["users"]
            
            self._connected = True
            logger.info("✅ Successfully connected to MongoDB!")
            logger.info(f"   Database: {self.db.name}")
            logger.info(f"   Collections: {self.db.list_collection_names()}")
            
        except Exception as e:
            logger.error(f"❌ MongoDB connection failed: {e}")
            self._connected = False
            # In development, you might want to continue without DB
            # In production, you should raise the exception
            raise e
    
    def disconnect(self):
        """Close the MongoDB connection"""
        if self.client:
            self.client.close()
            self._connected = False
            logger.info("📦 Disconnected from MongoDB")
    
    def is_connected(self) -> bool:
        """Check if database is connected"""
        return self._connected
    
    def get_users_collection(self) -> Collection:
        """Get users collection"""
        if not self._connected:
            raise RuntimeError("Database not connected")
        return self.users_collection
    
    def get_database(self) -> Database:
        """Get database instance"""
        if not self._connected:
            raise RuntimeError("Database not connected")
        return self.db

# Create global database manager instance
db_manager = DatabaseManager()

def get_database() -> Database:
    """Dependency to get database instance"""
    return db_manager.get_database()

def get_users_collection() -> Collection:
    """Dependency to get users collection"""
    return db_manager.get_users_collection()