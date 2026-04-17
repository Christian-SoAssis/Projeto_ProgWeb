from app.domain.entities.bid import Bid as BidEntity, BidStatus
from app.domain.entities.professional import Professional as ProfessionalEntity, Category as CategoryEntity
from app.domain.entities.request import Request as RequestEntity, RequestImage as RequestImageEntity, RequestStatus
from app.domain.entities.contract import Contract as ContractEntity, ContractStatus
from app.domain.entities.user import User as UserEntity, UserRole
from app.domain.entities.lgpd import ConsentLog as ConsentEntity
from app.domain.entities.review import Review as ReviewEntity
from app.domain.entities.favorite import Favorite as FavoriteEntity

from app.models.bid import Bid as BidModel
from app.models.professional import Professional as ProfessionalModel
from app.models.request import Request as RequestModel, RequestImage as RequestImageModel
from app.models.contract import Contract as ContractModel
from app.models.user import User as UserModel
from app.models.category import Category as CategoryModel
from app.models.lgpd import ConsentLog as ConsentModel
from app.models.review import Review as ReviewModel
from app.models.favorite import Favorite as FavoriteModel

class BidMapper:
    @staticmethod
    def to_entity(model: BidModel) -> BidEntity:
        return BidEntity(
            id=model.id,
            request_id=model.request_id,
            professional_id=model.professional_id,
            price_cents=model.price_cents,
            message=model.message,
            status=BidStatus(model.status) if model.status else BidStatus.PENDING,
            created_at=model.created_at,
            professional_name=getattr(model.professional.user, "name", None) if model.professional and model.professional.user else None,
            professional_avatar=getattr(model.professional.user, "avatar_url", None) if model.professional and model.professional.user else None
        )

    @staticmethod
    def to_model(entity: BidEntity) -> BidModel:
        return BidModel(
            id=entity.id,
            request_id=entity.request_id,
            professional_id=entity.professional_id,
            price_cents=entity.price_cents,
            message=entity.message,
            status=entity.status.value if hasattr(entity.status, "value") else entity.status,
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
            is_active=model.is_active
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
            is_active=entity.is_active
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
            latitude=model.latitude,
            longitude=model.longitude,
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
            document_path=entity.document_path,
            latitude=entity.latitude,
            longitude=entity.longitude
        )

class RequestImageMapper:
    @staticmethod
    def to_entity(model: RequestImageModel) -> RequestImageEntity:
        return RequestImageEntity(
            id=model.id,
            request_id=model.request_id,
            url=model.url,
            content_type=model.content_type,
            size_bytes=model.size_bytes,
            analyzed=model.analyzed,
            created_at=model.created_at
        )

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
        return RequestEntity(
            id=model.id,
            client_id=model.client_id,
            category_id=model.category_id,
            title=model.title,
            description=model.description,
            latitude=model.latitude,
            longitude=model.longitude,
            urgency=model.urgency,
            budget_cents=model.budget_cents,
            status=RequestStatus(model.status) if model.status else RequestStatus.OPEN,
            ai_complexity=model.ai_complexity,
            ai_urgency=model.ai_urgency,
            ai_specialties=model.ai_specialties,
            created_at=model.created_at,
            updated_at=model.updated_at,
            images=[RequestImageMapper.to_entity(img) for img in getattr(model, "images", [])],
            category_name=getattr(model.category, "name", None) if hasattr(model, "category") else None,
            client_name=getattr(model.client, "name", None) if hasattr(model, "client") else None
        )

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
        return ContractEntity(
            id=model.id,
            request_id=model.request_id,
            client_id=model.client_id,
            professional_id=model.professional_id,
            agreed_cents=model.agreed_cents,
            status=ContractStatus(model.status) if isinstance(model.status, str) else model.status,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    @staticmethod
    def to_model(entity: ContractEntity) -> ContractModel:
        return ContractModel(
            id=entity.id,
            request_id=entity.request_id,
            client_id=entity.client_id,
            professional_id=entity.professional_id,
            agreed_cents=entity.agreed_cents,
            status=entity.status.value if hasattr(entity.status, "value") else entity.status,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )

class CategoryMapper:
    @staticmethod
    def to_entity(model: CategoryModel) -> CategoryEntity:
        return CategoryEntity(
            id=model.id,
            name=model.name,
            slug=model.slug,
            color=model.color
        )

    @staticmethod
    def to_model(entity: CategoryEntity) -> CategoryModel:
        return CategoryModel(
            id=entity.id,
            name=entity.name,
            slug=entity.slug,
            color=entity.color
        )

class ConsentMapper:
    @staticmethod
    def to_entity(model: ConsentModel) -> ConsentEntity:
        return ConsentEntity(
            id=model.id,
            user_id=model.user_id,
            consent_type=model.consent_type,
            is_granted=model.is_granted,
            ip_address=model.ip_address,
            user_agent=model.user_agent,
            accepted_at=model.accepted_at
        )

    @staticmethod
    def to_model(entity: ConsentEntity) -> ConsentModel:
        return ConsentModel(
            id=entity.id,
            user_id=entity.user_id,
            consent_type=entity.consent_type,
            is_granted=entity.is_granted,
            ip_address=entity.ip_address,
            user_agent=entity.user_agent,
            accepted_at=entity.accepted_at
        )

class ReviewMapper:
    @staticmethod
    def to_entity(model: ReviewModel) -> ReviewEntity:
        return ReviewEntity(
            id=model.id,
            contract_id=model.contract_id,
            reviewer_id=model.reviewer_id,
            reviewee_id=model.reviewee_id,
            rating=model.rating,
            text=model.text,
            is_authentic=model.is_authentic,
            created_at=model.created_at,
            score_punctuality=model.score_punctuality,
            score_quality=model.score_quality,
            score_cleanliness=model.score_cleanliness,
            score_communication=model.score_communication
        )

    @staticmethod
    def to_model(entity: ReviewEntity) -> ReviewModel:
        return ReviewModel(
            id=entity.id,
            contract_id=entity.contract_id,
            reviewer_id=entity.reviewer_id,
            reviewee_id=entity.reviewee_id,
            rating=entity.rating,
            text=entity.text,
            is_authentic=entity.is_authentic,
            created_at=entity.created_at,
            score_punctuality=entity.score_punctuality,
            score_quality=entity.score_quality,
            score_cleanliness=entity.score_cleanliness,
            score_communication=entity.score_communication
        )

class FavoriteMapper:
    @staticmethod
    def to_entity(model: FavoriteModel) -> FavoriteEntity:
        return FavoriteEntity(
            id=model.id,
            client_id=model.client_id,
            professional_id=model.professional_id,
            created_at=model.created_at
        )

    @staticmethod
    def to_model(entity: FavoriteEntity) -> FavoriteModel:
        return FavoriteModel(
            id=entity.id,
            client_id=entity.client_id,
            professional_id=entity.professional_id,
            created_at=entity.created_at
        )
