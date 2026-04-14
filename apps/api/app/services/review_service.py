"""
Review Service — lógica de negócio para reviews e reputação.

Regras:
- Apenas cliente dono do contrato pode criar review
- Contrato deve ter status='completed'
- 1 review por contrato (unique constraint)
- Após criar review autêntica: recalcular reputation_score do profissional
- NLP de scores por dimensão: via Gemini (BERTimbau = stub por ora)

Fórmula reputation_score (escala 0-5):
  score = (0.3*avg_quality + 0.25*avg_punctuality
           + 0.2*avg_communication + 0.15*avg_cleanliness
           + 0.1*min(completed_jobs/50, 1.0)) * 5
"""
import logging
import uuid
import json
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import HTTPException, status

from app.models.review import Review
from app.models.contract import Contract
from app.models.professional import Professional
from app.core.config import settings

logger = logging.getLogger(__name__)


def calculate_reputation_score(
    avg_quality: float,
    avg_punctuality: float,
    avg_communication: float,
    avg_cleanliness: float,
    completed_jobs: int,
) -> float:
    """Calcula reputation_score na escala 0-5."""
    jobs_factor = min(completed_jobs / 50.0, 1.0)
    raw = (
        0.30 * avg_quality
        + 0.25 * avg_punctuality
        + 0.20 * avg_communication
        + 0.15 * avg_cleanliness
        + 0.10 * jobs_factor
    )
    return round(raw * 5.0, 4)


def is_review_authentic(text: str) -> bool:
    """
    Detecção básica de reviews inautênticas.
    Regras simples:
    - Texto muito curto (< 20 chars) -> suspeito
    - Texto com repetição excessiva de palavras -> suspeito
    """
    if len(text.strip()) < 20:
        return False

    words = text.lower().split()
    if len(words) > 3:
        unique_ratio = len(set(words)) / len(words)
        if unique_ratio < 0.4:  # mais de 60% das palavras repetidas
            return False

    return True


async def _analyze_with_gemini(text: str) -> dict:
    """
    Analisa texto da review com Gemini para extrair scores por dimensão.
    Retorna dict com keys: punctuality, quality, cleanliness, communication (0.0-1.0).
    """
    if not settings.GOOGLE_API_KEY or settings.GOOGLE_API_KEY == "[ENCRYPTION_KEY]":
        logger.warning("GOOGLE_API_KEY não configurada para análise NLP.")
        # Fallback para scores médios para permitir que o sistema funcione sem IA
        return {
            "punctuality": 0.8,
            "quality": 0.8,
            "cleanliness": 0.8,
            "communication": 0.8
        }

    try:
        from google import genai
        from google.genai import types
        
        client = genai.Client(api_key=settings.GOOGLE_API_KEY)
        
        prompt = f"""Analise esta avaliação de serviço e extraia scores de 0.0 a 1.0 para cada dimensão.
Retorne APENAS um JSON válido, sem markdown, sem explicações:
{{"punctuality": <float>, "quality": <float>, "cleanliness": <float>, "communication": <float>}}

Avaliação: "{text}"
"""
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        
        if not response.text:
            return {}
            
        scores = json.loads(response.text.strip())

        # Validar e clamp 0-1
        result = {}
        for key in ["punctuality", "quality", "cleanliness", "communication"]:
            val = float(scores.get(key, 0.5))
            result[key] = max(0.0, min(1.0, val))
        return result

    except Exception as e:
        logger.error(f"Gemini NLP falhou para review: {e}")
        return {
            "punctuality": 0.7,
            "quality": 0.7,
            "cleanliness": 0.7,
            "communication": 0.7
        }


async def _recalculate_reputation(db: AsyncSession, professional_id: uuid.UUID) -> None:
    """Recalcula e atualiza reputation_score do profissional."""
    # Buscar médias das reviews autênticas com scores preenchidos
    result = await db.execute(
        select(
            func.avg(Review.score_quality).label("avg_quality"),
            func.avg(Review.score_punctuality).label("avg_punctuality"),
            func.avg(Review.score_communication).label("avg_communication"),
            func.avg(Review.score_cleanliness).label("avg_cleanliness"),
            func.count(Review.id).label("total"),
        )
        .join(Contract, Review.contract_id == Contract.id)
        .where(
            Contract.professional_id == professional_id,
            Review.is_authentic == True,
            Review.score_quality.isnot(None),
        )
    )
    row = result.one()

    if not row.total or row.total == 0:
        return

    # Buscar completed_jobs (contratos completed)
    jobs_result = await db.execute(
        select(func.count(Contract.id))
        .where(
            Contract.professional_id == professional_id,
            Contract.status == "completed",
        )
    )
    completed_jobs = jobs_result.scalar() or 0

    new_score = calculate_reputation_score(
        avg_quality=float(row.avg_quality or 0),
        avg_punctuality=float(row.avg_punctuality or 0),
        avg_communication=float(row.avg_communication or 0),
        avg_cleanliness=float(row.avg_cleanliness or 0),
        completed_jobs=completed_jobs,
    )

    # Atualizar professional
    prof_result = await db.execute(
        select(Professional).where(Professional.id == professional_id)
    )
    prof = prof_result.scalar_one_or_none()
    if prof:
        prof.reputation_score = new_score


async def create_review(
    db: AsyncSession,
    client_user_id: uuid.UUID,
    contract_id: uuid.UUID,
    rating: int,
    text: str,
) -> Review:
    # 1. Buscar contrato e profissional associado
    result = await db.execute(
        select(Contract).where(Contract.id == contract_id)
    )
    contract = result.scalar_one_or_none()
    if not contract:
        raise HTTPException(status_code=404, detail="Contrato não encontrado")

    # 2. Verificar ownership
    if str(contract.client_id) != str(client_user_id):
        raise HTTPException(status_code=403, detail="Acesso negado")

    # 3. Verificar status do contrato
    if contract.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Contrato não finalizado — pagamento pendente"
        )

    # 4. Verificar autenticidade
    authentic = is_review_authentic(text)

    # Buscar Professional record para obter o user_id (reviewee_id)
    prof_result = await db.execute(
        select(Professional).where(Professional.id == contract.professional_id)
    )
    prof = prof_result.scalar_one_or_none()
    if not prof:
        raise HTTPException(status_code=404, detail="Profissional não encontrado")

    # 5. Criar review
    review = Review(
        contract_id=contract_id,
        reviewer_id=client_user_id,
        reviewee_id=prof.user_id,
        rating=rating,
        text=text,
        is_authentic=authentic,
    )
    db.add(review)

    try:
        await db.flush()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe uma avaliação para este contrato"
        )

    # 6. Análise NLP (Gemini) — atualizar scores (fazemos síncrono por ora como solicitado)
    if authentic:
        scores = await _analyze_with_gemini(text)
        if scores:
            review.score_punctuality = scores.get("punctuality")
            review.score_quality = scores.get("quality")
            review.score_cleanliness = scores.get("cleanliness")
            review.score_communication = scores.get("communication")
            await db.flush()

            # 7. Recalcular reputation_score do profissional
            await _recalculate_reputation(db, contract.professional_id)

    return review


async def list_reviews_for_professional(
    db: AsyncSession,
    professional_id: uuid.UUID,
) -> List[Review]:
    """Lista reviews autênticas de um profissional."""
    result = await db.execute(
        select(Review)
        .join(Contract, Review.contract_id == Contract.id)
        .where(
            Contract.professional_id == professional_id,
            Review.is_authentic == True,
        )
        .order_by(Review.created_at.desc())
    )
    return list(result.scalars().all())
