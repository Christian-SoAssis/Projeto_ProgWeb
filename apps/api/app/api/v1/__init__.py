from fastapi import APIRouter
 
from app.api.v1.auth import router as auth_router
from app.api.v1.professionals import router as professionals_router
from app.api.v1.admin import router as admin_router
from app.api.v1.requests import router as requests_router
from app.api.v1.bids import router as bids_router
from app.api.v1.reviews import router as reviews_router
from app.api.v1.search import router as search_router
from app.api.v1.professionals_panel import router as professionals_panel_router
from app.api.v1.favorites import router as favorites_router
from app.api.v1.notifications import router as notifications_router

router = APIRouter()

@router.get("/")
async def v1_root():
    return {"message": "Bem-vindo à API v1 do ServiçoJá!"}

router.include_router(auth_router)
router.include_router(professionals_router)
router.include_router(admin_router)
router.include_router(requests_router)
router.include_router(bids_router)
router.include_router(reviews_router)
router.include_router(search_router)
router.include_router(professionals_panel_router)
router.include_router(favorites_router)
router.include_router(notifications_router)
