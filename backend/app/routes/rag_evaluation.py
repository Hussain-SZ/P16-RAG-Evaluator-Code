from fastapi import APIRouter, HTTPException, status
from backend.app.schemas.rag_evaluation import RAGEvaluationRequest, RAGEvaluationResponse
from backend.app.services.rag_evaluation_service import rag_evaluation_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/evaluate", response_model=RAGEvaluationResponse, status_code=status.HTTP_200_OK)
async def evaluate_rag_response(request: RAGEvaluationRequest):
    """
    Evaluate a RAG (Retrieval-Augmented Generation) response for faithfulness.
    
    This endpoint evaluates how faithful an LLM-generated answer is to the provided context
    by analyzing each sentence and classifying it as faithful, inferred, extrapolated, or hallucinated.
    
    Args:
        request: RAGEvaluationRequest containing query, context, and llm_output
        
    Returns:
        RAGEvaluationResponse with evaluation results and metrics
        
    Raises:
        HTTPException: If evaluation fails due to API or processing errors
    """
    try:
        logger.info("Starting RAG evaluation")
        
        # Call the evaluation service
        result = await rag_evaluation_service.evaluate_faithfulness(
            query=request.query,
            context=request.context,
            llm_output=request.llm_output
        )
        
        # Check if evaluation was successful
        if result.get("status") == "error":
            logger.error(f"RAG evaluation failed: {result.get('error')}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Evaluation failed: {result.get('error')}"
            )
        
        logger.info("RAG evaluation completed successfully")
        return RAGEvaluationResponse(**result)
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error in RAG evaluation endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during evaluation"
        )


@router.get("/health")
async def rag_evaluation_health():
    """Health check for RAG evaluation service"""
    try:
        # Check if the service can be initialized (basic health check)
        service_status = "healthy" if rag_evaluation_service else "unhealthy"
        
        return {
            "status": service_status,
            "service": "RAG Evaluation",
            "message": "RAG evaluation service is running"
        }
    except Exception as e:
        logger.error(f"RAG evaluation health check failed: {e}")
        return {
            "status": "unhealthy", 
            "service": "RAG Evaluation",
            "error": str(e)
        }