from fastapi import APIRouter

from app.api.v1.auth import router as auth_router

router = APIRouter()

@router.get("/")
async def v1_root():
    return {"message": "Bem-vindo à API v1 do ServiçoJá!"}

router.include_router(auth_router)
