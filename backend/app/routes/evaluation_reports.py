from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Optional
from backend.app.schemas.evaluation_reports import (
    SaveReportRequest, SaveReportResponse, ReportSummary, 
    ReportDetailResponse, UpdateReportRequest
)
from backend.app.database.evaluation_report_repository import evaluation_report_repository
from backend.app.core.security import get_current_user
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/save", response_model=SaveReportResponse, status_code=status.HTTP_201_CREATED)
async def save_evaluation_report(
    request: SaveReportRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Save an evaluation report for later viewing
    
    Requires authentication. Saves the complete evaluation including:
    - Original inputs (query, context, answer)
    - Evaluation results (metrics and sentence classifications)
    - User metadata (name, tags, notes)
    """
    try:
        logger.info(f"Saving report for user {current_user['user_id']}")
        
        # Prepare report data
        report_data = {
            "user_id": current_user["user_id"],
            "report_name": request.report_name,
            "query": request.query,
            "context": request.context,
            "llm_output": request.llm_output,
            "aggregate_metrics": request.aggregate_metrics,
            "sentence_evaluations": request.sentence_evaluations,
            "tags": request.tags or [],
            "notes": request.notes or "",
            "created_at": datetime.utcnow()
        }
        
        # Save to database
        report_id = evaluation_report_repository.save_report(report_data)
        
        logger.info(f"Report saved successfully with ID: {report_id}")
        
        return SaveReportResponse(
            report_id=report_id,
            message="Report saved successfully",
            created_at=report_data["created_at"]
        )
        
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database not available: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Failed to save report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save report: {str(e)}"
        )


@router.get("/my-reports", response_model=List[ReportSummary])
async def get_my_reports(
    limit: int = 50,
    skip: int = 0,
    tags: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Get all saved reports for the current user
    
    Returns a list of report summaries with key metrics.
    Use query parameters for pagination and filtering by tags.
    """
    try:
        logger.info(f"Fetching reports for user {current_user['user_id']}")
        
        # Parse tags if provided
        tag_list = tags.split(",") if tags else None
        
        # Get reports from database
        reports = evaluation_report_repository.get_reports_by_user(
            user_id=current_user["user_id"],
            limit=limit,
            skip=skip,
            tags=tag_list
        )
        
        # Convert to summary format
        summaries = []
        for report in reports:
            metrics = report.get("aggregate_metrics", {})
            summaries.append(ReportSummary(
                report_id=report["_id"],
                report_name=report["report_name"],
                faithfulness_rate=metrics.get("faithfulness_rate", 0),
                hallucination_rate=metrics.get("hallucination_rate", 0),
                total_sentences=metrics.get("total_sentences", 0),
                created_at=report["created_at"],
                tags=report.get("tags", [])
            ))
        
        logger.info(f"Retrieved {len(summaries)} reports")
        return summaries
        
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database not available: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Failed to fetch reports: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch reports: {str(e)}"
        )


@router.get("/report/{report_id}", response_model=ReportDetailResponse)
async def get_report_details(
    report_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get full details of a specific report
    
    Returns complete evaluation data including all inputs and results.
    Only the report owner can access it.
    """
    try:
        logger.info(f"Fetching report {report_id} for user {current_user['user_id']}")
        
        # Get report from database
        report = evaluation_report_repository.get_report_by_id(report_id)
        
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found"
            )
        
        # Verify ownership
        if report["user_id"] != current_user["user_id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this report"
            )
        
        # Return full details
        return ReportDetailResponse(
            report_id=report["_id"],
            report_name=report["report_name"],
            query=report["query"],
            context=report["context"],
            llm_output=report["llm_output"],
            aggregate_metrics=report["aggregate_metrics"],
            sentence_evaluations=report["sentence_evaluations"],
            created_at=report["created_at"],
            tags=report.get("tags", []),
            notes=report.get("notes", "")
        )
        
    except HTTPException:
        raise
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database not available: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Failed to fetch report {report_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch report: {str(e)}"
        )


@router.patch("/report/{report_id}", response_model=dict)
async def update_report(
    report_id: str,
    update_data: UpdateReportRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Update report metadata (name, tags, notes)
    
    Only the report owner can update it.
    """
    try:
        logger.info(f"Updating report {report_id} for user {current_user['user_id']}")
        
        # First verify the report exists and user owns it
        report = evaluation_report_repository.get_report_by_id(report_id)
        
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found"
            )
        
        if report["user_id"] != current_user["user_id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update this report"
            )
        
        # Update the report
        update_dict = update_data.model_dump(exclude_none=True)
        success = evaluation_report_repository.update_report(report_id, update_dict)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update report"
            )
        
        return {"message": "Report updated successfully"}
        
    except HTTPException:
        raise
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database not available: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Failed to update report {report_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update report: {str(e)}"
        )


@router.delete("/report/{report_id}", response_model=dict)
async def delete_report(
    report_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a saved report
    
    Only the report owner can delete it.
    """
    try:
        logger.info(f"Deleting report {report_id} for user {current_user['user_id']}")
        
        # Delete the report (repository checks ownership)
        success = evaluation_report_repository.delete_report(
            report_id=report_id,
            user_id=current_user["user_id"]
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found or you don't have permission to delete it"
            )
        
        return {"message": "Report deleted successfully"}
        
    except HTTPException:
        raise
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database not available: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Failed to delete report {report_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete report: {str(e)}"
        )


@router.get("/stats", response_model=dict)
async def get_report_stats(current_user: dict = Depends(get_current_user)):
    """
    Get statistics about user's saved reports
    """
    try:
        total_reports = evaluation_report_repository.count_user_reports(
            current_user["user_id"]
        )
        
        return {
            "total_reports": total_reports,
            "user_id": current_user["user_id"]
        }
        
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database not available: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stats: {str(e)}"
        )
