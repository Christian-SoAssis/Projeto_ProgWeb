from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.infrastructure.database.repositories.bid_repository_impl import BidRepositoryImpl
from app.infrastructure.database.repositories.professional_repository_impl import ProfessionalRepositoryImpl
from app.infrastructure.database.repositories.request_repository_impl import RequestRepositoryImpl
from app.infrastructure.database.repositories.contract_repository_impl import ContractRepositoryImpl

from app.application.use_cases.create_bid_use_case import CreateBidUseCase
from app.application.use_cases.update_bid_use_case import UpdateBidUseCase
from app.application.use_cases.create_request_use_case import CreateRequestUseCase
from app.application.use_cases.get_request_use_case import GetRequestUseCase
from app.application.use_cases.list_requests_use_case import ListRequestsUseCase
from app.infrastructure.services.local_image_storage import LocalImageStorage
from app.infrastructure.services.arq_task_queue import ArqTaskQueue

def get_create_bid_use_case(db: AsyncSession = Depends(get_db)) -> CreateBidUseCase:
    bid_repo = BidRepositoryImpl(db)
    prof_repo = ProfessionalRepositoryImpl(db)
    req_repo = RequestRepositoryImpl(db)
    return CreateBidUseCase(bid_repo, prof_repo, req_repo)

def get_update_bid_use_case(db: AsyncSession = Depends(get_db)) -> UpdateBidUseCase:
    bid_repo = BidRepositoryImpl(db)
    contract_repo = ContractRepositoryImpl(db)
    req_repo = RequestRepositoryImpl(db)
    return UpdateBidUseCase(bid_repo, contract_repo, req_repo)

def get_create_request_use_case(db: AsyncSession = Depends(get_db)) -> CreateRequestUseCase:
    req_repo = RequestRepositoryImpl(db)
    image_storage = LocalImageStorage()
    task_queue = ArqTaskQueue()
    return CreateRequestUseCase(req_repo, image_storage, task_queue)

def get_request_use_case(db: AsyncSession = Depends(get_db)) -> GetRequestUseCase:
    req_repo = RequestRepositoryImpl(db)
    return GetRequestUseCase(req_repo)

def get_list_requests_use_case(db: AsyncSession = Depends(get_db)) -> ListRequestsUseCase:
    req_repo = RequestRepositoryImpl(db)
    return ListRequestsUseCase(req_repo)
