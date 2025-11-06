from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from bson import ObjectId


class PyObjectId(str):
    """Custom type for MongoDB ObjectId"""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return str(v)


class SavedEvaluationReport(BaseModel):
    """Model for saved RAG evaluation reports"""
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    user_id: str = Field(..., description="ID of user who created the report")
    report_name: str = Field(..., description="User-given name for the report")
    
    # Original inputs
    query: str = Field(..., description="Original query")
    context: str = Field(..., description="Context used for evaluation")
    llm_output: str = Field(..., description="LLM-generated answer")
    
    # Evaluation results
    aggregate_metrics: Dict[str, Any] = Field(..., description="Aggregate metrics")
    sentence_evaluations: List[Dict[str, Any]] = Field(..., description="Sentence-level evaluations")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    tags: Optional[List[str]] = Field(default=[], description="User-defined tags")
    notes: Optional[str] = Field(default="", description="User notes about the evaluation")
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}
        arbitrary_types_allowed = True
