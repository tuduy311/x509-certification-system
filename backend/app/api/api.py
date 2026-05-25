from fastapi import APIRouter
from app.api.endpoints import auth, admin, customer

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(customer.router, prefix="/customer", tags=["customer"])
