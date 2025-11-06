from fastapi import APIRouter
from backend.app.api import auth, protected
from backend.app.routes import rag_evaluation, evaluation_reports

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(protected.router, prefix="/protected", tags=["Protected"])
api_router.include_router(rag_evaluation.router, prefix="/rag", tags=["RAG Evaluation"])
api_router.include_router(evaluation_reports.router, prefix="/reports", tags=["Evaluation Reports"])