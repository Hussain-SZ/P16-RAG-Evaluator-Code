from fastapi import APIRouter
from backend.app.api import auth, protected

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(protected.router, prefix="/protected", tags=["Protected"])