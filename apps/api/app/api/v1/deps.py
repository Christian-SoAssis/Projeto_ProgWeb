import uuid
from typing import List, Optional
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.infrastructure.database.repositories.bid_repository_impl import BidRepositoryImpl
from app.infrastructure.database.repositories.professional_repository_impl import ProfessionalRepositoryImpl
from app.infrastructure.database.repositories.request_repository_impl import RequestRepositoryImpl
from app.infrastructure.database.repositories.contract_repository_impl import ContractRepositoryImpl
from app.infrastructure.database.repositories.user_repository_impl import UserRepositoryImpl
from app.infrastructure.database.repositories.consent_repository_impl import ConsentRepositoryImpl
from app.infrastructure.database.repositories.category_repository_impl import CategoryRepositoryImpl
from app.infrastructure.database.repositories.review_repository_impl import ReviewRepositoryImpl
from app.infrastructure.database.repositories.favorite_repository_impl import FavoriteRepositoryImpl

from app.application.use_cases.create_bid_use_case import CreateBidUseCase
from app.application.use_cases.update_bid_use_case import UpdateBidUseCase
from app.application.use_cases.create_request_use_case import CreateRequestUseCase
from app.application.use_cases.get_request_use_case import GetRequestUseCase
from app.application.use_cases.list_requests_use_case import ListRequestsUseCase
from app.application.use_cases.register_professional_use_case import RegisterProfessionalUseCase
from app.application.use_cases.get_professional_use_case import GetProfessionalUseCase
from app.application.use_cases.list_categories_use_case import ListCategoriesUseCase
from app.application.use_cases.register_client_use_case import RegisterClientUseCase
from app.application.use_cases.login_use_case import LoginUseCase
from app.application.use_cases.create_review_use_case import CreateReviewUseCase
from app.application.use_cases.list_professional_reviews_use_case import ListProfessionalReviewsUseCase
from app.application.use_cases.add_favorite_use_case import AddFavoriteUseCase
from app.application.use_cases.list_favorites_use_case import ListFavoritesUseCase
from app.application.use_cases.remove_favorite_use_case import RemoveFavoriteUseCase

from app.infrastructure.services.local_image_storage import LocalImageStorage
from app.infrastructure.services.arq_task_queue import ArqTaskQueue

# Repositories
async def get_bid_repository(db: AsyncSession = Depends(get_db)):
    return BidRepositoryImpl(db)

async def get_professional_repository(db: AsyncSession = Depends(get_db)):
    return ProfessionalRepositoryImpl(db)

async def get_request_repository(db: AsyncSession = Depends(get_db)):
    return RequestRepositoryImpl(db)

async def get_contract_repository(db: AsyncSession = Depends(get_db)):
    return ContractRepositoryImpl(db)

async def get_user_repository(db: AsyncSession = Depends(get_db)):
    return UserRepositoryImpl(db)

async def get_consent_repository(db: AsyncSession = Depends(get_db)):
    return ConsentRepositoryImpl(db)

async def get_category_repository(db: AsyncSession = Depends(get_db)):
    return CategoryRepositoryImpl(db)

async def get_review_repository(db: AsyncSession = Depends(get_db)):
    return ReviewRepositoryImpl(db)

async def get_favorite_repository(db: AsyncSession = Depends(get_db)):
    return FavoriteRepositoryImpl(db)

# Services
async def get_image_storage():
    return LocalImageStorage()

async def get_task_queue():
    return ArqTaskQueue()

# Use Cases
async def get_create_bid_use_case(
    bid_repo = Depends(get_bid_repository),
    prof_repo = Depends(get_professional_repository),
    req_repo = Depends(get_request_repository)
):
    return CreateBidUseCase(bid_repo, prof_repo, req_repo)

async def get_update_bid_use_case(
    bid_repo = Depends(get_bid_repository),
    contract_repo = Depends(get_contract_repository),
    req_repo = Depends(get_request_repository)
):
    return UpdateBidUseCase(bid_repo, contract_repo, req_repo)

async def get_create_request_use_case(
    req_repo = Depends(get_request_repository),
    image_storage = Depends(get_image_storage),
    task_queue = Depends(get_task_queue)
):
    return CreateRequestUseCase(req_repo, image_storage, task_queue)

async def get_request_use_case(req_repo = Depends(get_request_repository)):
    return GetRequestUseCase(req_repo)

async def get_list_requests_use_case(req_repo = Depends(get_request_repository)):
    return ListRequestsUseCase(req_repo)

async def get_register_professional_use_case(
    user_repo = Depends(get_user_repository),
    prof_repo = Depends(get_professional_repository),
    consent_repo = Depends(get_consent_repository),
    file_storage = Depends(get_image_storage)
):
    return RegisterProfessionalUseCase(user_repo, prof_repo, consent_repo, file_storage)

async def get_professional_use_case(prof_repo = Depends(get_professional_repository)):
    return GetProfessionalUseCase(prof_repo)

async def get_list_categories_use_case(repo = Depends(get_category_repository)):
    return ListCategoriesUseCase(repo)

async def get_register_client_use_case(
    user_repo = Depends(get_user_repository),
    consent_repo = Depends(get_consent_repository)
):
    return RegisterClientUseCase(user_repo, consent_repo)

async def get_login_use_case(user_repo = Depends(get_user_repository)):
    return LoginUseCase(user_repo)

# Reviews & Favorites
async def get_create_review_use_case(
    review_repo = Depends(get_review_repository),
    contract_repo = Depends(get_contract_repository),
    prof_repo = Depends(get_professional_repository)
):
    return CreateReviewUseCase(review_repo, contract_repo, prof_repo)

async def get_list_professional_reviews_use_case(
    review_repo = Depends(get_review_repository)
):
    return ListProfessionalReviewsUseCase(review_repo)

async def get_add_favorite_use_case(
    favorite_repo = Depends(get_favorite_repository)
):
    return AddFavoriteUseCase(favorite_repo)

async def get_list_favorites_use_case(
    favorite_repo = Depends(get_favorite_repository)
):
    return ListFavoritesUseCase(favorite_repo)

async def get_remove_favorite_use_case(
    favorite_repo = Depends(get_favorite_repository)
):
    return RemoveFavoriteUseCase(favorite_repo)
