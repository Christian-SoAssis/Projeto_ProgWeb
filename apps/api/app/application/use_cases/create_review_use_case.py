import uuid
import logging
import json
from dataclasses import dataclass
from typing import Optional
from app.domain.entities.review import Review
from app.domain.repositories.review_repository import ReviewRepository
from app.domain.repositories.contract_repository import ContractRepository
from app.domain.repositories.professional_repository import ProfessionalRepository
from app.domain.exceptions import EntityNotFoundError, BusinessRuleViolationError
from app.core.config import settings

logger = logging.getLogger(__name__)

@dataclass
class CreateReviewInput:
    client_user_id: uuid.UUID
    contract_id: uuid.UUID
    rating: int
    text: str

class CreateReviewUseCase:
    def __init__(
        self,
        review_repo: ReviewRepository,
        contract_repo: ContractRepository,
        prof_repo: ProfessionalRepository
    ):
        self.review_repo = review_repo
        self.contract_repo = contract_repo
        self.prof_repo = prof_repo

    async def execute(self, input_data: CreateReviewInput) -> Review:
        # 1. Buscar contrato
        contract = await self.contract_repo.get_by_id(input_data.contract_id)
        if not contract:
            raise EntityNotFoundError("Contrato não encontrado")

        # 2. Verificar ownership
        if contract.client_id != input_data.client_user_id:
            raise BusinessRuleViolationError("Acesso negado: apenas o cliente do contrato pode avaliar")

        # 3. Verificar status do contrato
        if contract.status.value != "completed" if hasattr(contract.status, "value") else contract.status != "completed":
            raise BusinessRuleViolationError("Contrato não finalizado")

        # 4. Verificar autenticidade
        is_authentic = self._is_review_authentic(input_data.text)

        # 5. Criar review
        review = Review(
            id=uuid.uuid4(),
            contract_id=input_data.contract_id,
            reviewer_id=input_data.client_user_id,
            reviewee_id=contract.professional_id, # Usando ID do profissional (mas no model é reviewee_id (User.id))
            # Wait, contract.professional_id is referring to Professional.id?
            # Let's check contract model.
            rating=input_data.rating,
            text=input_data.text,
            is_authentic=is_authentic
        )
        
        # Need to get reviewee_id (User.id) from Professional
        prof = await self.prof_repo.get_by_id(contract.professional_id)
        if not prof:
             raise EntityNotFoundError("Profissional não encontrado")
        review.reviewee_id = prof.user_id

        # 6. NLP Analysis if authentic
        if is_authentic:
            scores = await self._analyze_with_gemini(input_data.text)
            review.score_punctuality = scores.get("punctuality")
            review.score_quality = scores.get("quality")
            review.score_cleanliness = scores.get("cleanliness")
            review.score_communication = scores.get("communication")

        saved_review = await self.review_repo.save(review)

        # 7. Recalcular reputação se autêntica
        if is_authentic:
            await self._recalculate_reputation(contract.professional_id)

        return saved_review

    def _is_review_authentic(self, text: str) -> bool:
        if len(text.strip()) < 20:
            return False
        words = text.lower().split()
        if len(words) > 3:
            unique_ratio = len(set(words)) / len(words)
            if unique_ratio < 0.4:
                return False
        return True

    async def _analyze_with_gemini(self, text: str) -> dict:
        if not settings.GOOGLE_API_KEY or settings.GOOGLE_API_KEY == "[ENCRYPTION_KEY]":
            return {"punctuality": 0.8, "quality": 0.8, "cleanliness": 0.8, "communication": 0.8}
        try:
            from google import genai
            from google.genai import types
            client = genai.Client(api_key=settings.GOOGLE_API_KEY)
            prompt = f"Analise esta avaliação e extraia scores de 0.0 a 1.0 para as dimensões: punctuality, quality, cleanliness, communication. Retorne APENAS um JSON: {text}"
            response = client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            return json.loads(response.text.strip())
        except Exception as e:
            logger.error(f"NLP error: {e}")
            return {"punctuality": 0.7, "quality": 0.7, "cleanliness": 0.7, "communication": 0.7}

    async def _recalculate_reputation(self, professional_id: uuid.UUID) -> None:
        from app.domain.services.reputation_service import calculate_reputation_score
        
        stats = await self.review_repo.get_averages(professional_id)
        if stats["total"] == 0:
            return
        
        completed_jobs = await self.contract_repo.count_completed_by_professional(professional_id)
        
        new_score = calculate_reputation_score(
            avg_quality=stats["avg_quality"],
            avg_punctuality=stats["avg_punctuality"],
            avg_communication=stats["avg_communication"],
            avg_cleanliness=stats["avg_cleanliness"],
            completed_jobs=completed_jobs
        )
        
        prof = await self.prof_repo.get_by_id(professional_id)
        if prof:
            prof.reputation_score = new_score
            await self.prof_repo.save(prof)
