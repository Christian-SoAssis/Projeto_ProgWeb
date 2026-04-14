import pytest
from app.services.review_service import calculate_reputation_score, is_review_authentic

def test_reputation_score_calculation():
    """
    score = (0.3*avg_quality + 0.25*avg_punctuality
            + 0.2*avg_communication + 0.15*avg_cleanliness
            + 0.1*min(completed_jobs/50, 1.0)) * 5
    """
    # Max possible score
    score = calculate_reputation_score(1.0, 1.0, 1.0, 1.0, 50)
    assert abs(score - 5.0) < 0.01

    # Zero score
    score = calculate_reputation_score(0.0, 0.0, 0.0, 0.0, 0)
    assert score == 0.0

    # Partial score (quality only)
    # 0.3 * 1.0 * 5 = 1.5
    score = calculate_reputation_score(1.0, 0.0, 0.0, 0.0, 0)
    assert abs(score - 1.5) < 0.01

def test_is_authentic_normal_text():
    assert is_review_authentic("Profissional muito competente e pontual.") is True

def test_is_authentic_too_short():
    # Texto < 20 chars -> inautêntico
    assert is_review_authentic("Ótimo!") is False

def test_is_authentic_generic_text():
    # Repetição excessiva
    assert is_review_authentic("bom bom bom bom bom bom bom bom bom") is False
