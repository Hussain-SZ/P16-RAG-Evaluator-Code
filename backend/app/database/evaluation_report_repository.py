from typing import List, Optional, Dict, Any
from bson import ObjectId
from datetime import datetime
from backend.app.database.connection import db_manager
import logging

logger = logging.getLogger(__name__)


class EvaluationReportRepository:
    """Repository for evaluation report database operations"""
    
    def __init__(self):
        """Initialize repository"""
        pass
    
    def _get_collection(self):
        """Get the reports collection"""
        if not db_manager.is_connected():
            raise RuntimeError("Database not connected")
        return db_manager.get_database()["evaluation_reports"]
    
    def save_report(self, report_data: Dict[str, Any]) -> str:
        """Save a new evaluation report"""
        try:
            collection = self._get_collection()
            result = collection.insert_one(report_data)
            logger.info(f"Report saved with ID: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Failed to save report: {e}")
            raise
    
    def get_report_by_id(self, report_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific report by ID"""
        try:
            collection = self._get_collection()
            report = collection.find_one({"_id": ObjectId(report_id)})
            if report:
                report["_id"] = str(report["_id"])
            return report
        except Exception as e:
            logger.error(f"Failed to get report {report_id}: {e}")
            return None
    
    def get_reports_by_user(
        self, 
        user_id: str, 
        limit: int = 50,
        skip: int = 0,
        tags: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Get all reports for a user with optional filtering"""
        try:
            collection = self._get_collection()
            
            # Build query
            query = {"user_id": user_id}
            if tags:
                query["tags"] = {"$in": tags}
            
            # Execute query
            reports = list(
                collection.find(query)
                .sort("created_at", -1)
                .skip(skip)
                .limit(limit)
            )
            
            # Convert ObjectId to string
            for report in reports:
                report["_id"] = str(report["_id"])
            
            logger.info(f"Retrieved {len(reports)} reports for user {user_id}")
            return reports
            
        except Exception as e:
            logger.error(f"Failed to get reports for user {user_id}: {e}")
            return []
    
    def update_report(
        self, 
        report_id: str, 
        update_data: Dict[str, Any]
    ) -> bool:
        """Update report metadata (name, tags, notes)"""
        try:
            collection = self._get_collection()
            
            # Remove None values
            update_data = {k: v for k, v in update_data.items() if v is not None}
            
            if not update_data:
                return True
            
            result = collection.update_one(
                {"_id": ObjectId(report_id)},
                {"$set": update_data}
            )
            
            success = result.modified_count > 0
            if success:
                logger.info(f"Updated report {report_id}")
            return success
            
        except Exception as e:
            logger.error(f"Failed to update report {report_id}: {e}")
            return False
    
    def delete_report(self, report_id: str, user_id: str) -> bool:
        """Delete a report (only if owned by user)"""
        try:
            collection = self._get_collection()
            result = collection.delete_one({
                "_id": ObjectId(report_id),
                "user_id": user_id  # Ensure user owns the report
            })
            
            success = result.deleted_count > 0
            if success:
                logger.info(f"Deleted report {report_id}")
            return success
            
        except Exception as e:
            logger.error(f"Failed to delete report {report_id}: {e}")
            return False
    
    def count_user_reports(self, user_id: str) -> int:
        """Count total reports for a user"""
        try:
            collection = self._get_collection()
            return collection.count_documents({"user_id": user_id})
        except Exception as e:
            logger.error(f"Failed to count reports for user {user_id}: {e}")
            return 0


# Global repository instance
evaluation_report_repository = EvaluationReportRepository()
