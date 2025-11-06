from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class SaveReportRequest(BaseModel):
    """Request to save an evaluation report"""
    report_name: str = Field(..., description="Name for the report", min_length=1, max_length=200)
    query: str
    context: str
    llm_output: str
    aggregate_metrics: Dict[str, Any]
    sentence_evaluations: List[Dict[str, Any]]
    tags: Optional[List[str]] = Field(default=[], description="Tags for categorizing the report")
    notes: Optional[str] = Field(default="", description="Optional notes")
    
    class Config:
        json_schema_extra = {
            "example": {
                "report_name": "ML Query Evaluation - Nov 2024",
                "query": "What is machine learning?",
                "context": "Machine learning is...",
                "llm_output": "ML is AI that learns...",
                "aggregate_metrics": {"faithfulness_rate": 0.75},
                "sentence_evaluations": [],
                "tags": ["machine-learning", "test"],
                "notes": "Good faithfulness score"
            }
        }


class SaveReportResponse(BaseModel):
    """Response after saving a report"""
    report_id: str
    message: str
    created_at: datetime


class ReportSummary(BaseModel):
    """Summary of a saved report for listing"""
    report_id: str
    report_name: str
    faithfulness_rate: float
    hallucination_rate: float
    total_sentences: int
    created_at: datetime
    tags: List[str]


class ReportDetailResponse(BaseModel):
    """Full details of a saved report"""
    report_id: str
    report_name: str
    query: str
    context: str
    llm_output: str
    aggregate_metrics: Dict[str, Any]
    sentence_evaluations: List[Dict[str, Any]]
    created_at: datetime
    tags: List[str]
    notes: str


class UpdateReportRequest(BaseModel):
    """Request to update report metadata"""
    report_name: Optional[str] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None
