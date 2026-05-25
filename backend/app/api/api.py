from fastapi import APIRouter
from backend.app.api.endpoints import customer
from backend.app.api.endpoints import admin, auth

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(customer.router, prefix="/customer", tags=["customer"])
