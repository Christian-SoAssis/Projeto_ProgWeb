from app.domain.entities.bid import Bid as BidEntity
from app.domain.entities.professional import Professional as ProfessionalEntity, Category as CategoryEntity
from app.domain.entities.request import Request as RequestEntity, RequestImage as RequestImageEntity
from app.domain.entities.contract import Contract as ContractEntity
from app.domain.entities.user import User as UserEntity

from app.models.bid import Bid as BidModel
from app.models.professional import Professional as ProfessionalModel
from app.models.request import Request as RequestModel, RequestImage as RequestImageModel
from app.models.contract import Contract as ContractModel
from app.models.user import User as UserModel
from app.models.category import Category as CategoryModel

class BidMapper:
    @staticmethod
    def to_entity(model: BidModel) -> BidEntity:
        return BidEntity.model_validate(model)

    @staticmethod
    def to_model(entity: BidEntity) -> BidModel:
        return BidModel(
            id=entity.id,
            request_id=entity.request_id,
            professional_id=entity.professional_id,
            price_cents=entity.price_cents,
            estimated_hours=entity.estimated_hours,
            message=entity.message,
            status=entity.status,
            created_at=entity.created_at
        )

class UserMapper:
    @staticmethod
    def to_entity(model: UserModel) -> UserEntity:
        return UserEntity(
            id=model.id,
            name=model.name,
            email=model.email,
            phone=model.phone,
            password_hash=model.password_hash,
            role=model.role,
            is_active=model.is_active,
            is_verified=model.is_verified
        )

    @staticmethod
    def to_model(entity: UserEntity) -> UserModel:
        return UserModel(
            id=entity.id,
            name=entity.name,
            email=entity.email,
            phone=entity.phone,
            password_hash=entity.password_hash,
            role=entity.role,
            is_active=entity.is_active,
            is_verified=entity.is_verified
        )

class ProfessionalMapper:
    @staticmethod
    def to_entity(model: ProfessionalModel) -> ProfessionalEntity:
        return ProfessionalEntity(
            id=model.id,
            user_id=model.user_id,
            bio=model.bio,
            reputation_score=model.reputation_score,
            is_verified=model.is_verified,
            hourly_rate_cents=model.hourly_rate_cents,
            service_radius_km=model.service_radius_km,
            document_type=model.document_type,
            document_path=model.document_path,
            categories=[
                CategoryEntity(id=cat.id, name=cat.name, color=cat.color)
                for cat in getattr(model, "categories", [])
            ],
            name=getattr(model.user, "name", None) if hasattr(model, "user") else None,
            email=getattr(model.user, "email", None) if hasattr(model, "user") else None
        )

    @staticmethod
    def to_model(entity: ProfessionalEntity) -> ProfessionalModel:
        return ProfessionalModel(
            id=entity.id,
            user_id=entity.user_id,
            bio=entity.bio,
            reputation_score=entity.reputation_score,
            is_verified=entity.is_verified,
            hourly_rate_cents=entity.hourly_rate_cents,
            service_radius_km=entity.service_radius_km,
            document_type=entity.document_type,
            document_path=entity.document_path
        )

class RequestImageMapper:
    @staticmethod
    def to_entity(model: RequestImageModel) -> RequestImageEntity:
        return RequestImageEntity.model_validate(model)

    @staticmethod
    def to_model(entity: RequestImageEntity) -> RequestImageModel:
        return RequestImageModel(
            id=entity.id,
            request_id=entity.request_id,
            url=entity.url,
            content_type=entity.content_type,
            size_bytes=entity.size_bytes,
            analyzed=entity.analyzed,
            created_at=entity.created_at
        )

class RequestMapper:
    @staticmethod
    def to_entity(model: RequestModel) -> RequestEntity:
        # Pydantic will use the hybrid_properties latitude/longitude from the model
        return RequestEntity.model_validate(model)

    @staticmethod
    def to_model(entity: RequestEntity) -> RequestModel:
        point = f"POINT({entity.longitude} {entity.latitude})"
        return RequestModel(
            id=entity.id,
            client_id=entity.client_id,
            category_id=entity.category_id,
            title=entity.title,
            description=entity.description,
            location=point,
            urgency=entity.urgency,
            budget_cents=entity.budget_cents,
            status=entity.status,
            ai_complexity=entity.ai_complexity,
            ai_urgency=entity.ai_urgency,
            ai_specialties=entity.ai_specialties,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )

class ContractMapper:
    @staticmethod
    def to_entity(model: ContractModel) -> ContractEntity:
        return ContractEntity.model_validate(model)

    @staticmethod
    def to_model(entity: ContractEntity) -> ContractModel:
        return ContractModel(
            id=entity.id,
            request_id=entity.request_id,
            professional_id=entity.professional_id,
            client_id=entity.client_id,
            agreed_cents=entity.agreed_cents,
            status=entity.status,
            started_at=entity.started_at,
            completed_at=entity.completed_at
        )
