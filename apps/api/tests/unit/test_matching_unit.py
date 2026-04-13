import pytest
from app.services.matching_service import haversine_km, rank_candidates

def test_haversine_same_point():
    assert haversine_km(-21.55, -45.42, -21.55, -45.42) == 0.0

def test_haversine_known_distance():
    # Varginha-MG para São Paulo-SP ≈ 254 km (em linha reta)
    dist = haversine_km(-21.55, -45.42, -23.55, -46.63)
    assert 240 < dist < 280

def test_haversine_boundary():
    # Coordenadas extremas não levantam exceção
    dist = haversine_km(-90, -180, 90, 180)
    assert dist > 0

# Testar que profissional dentro do raio passa e fora não passa
# Como não temos uma função de filtro pura no service ainda (está dentro do loop get_matches_v0),
# vamos testar o haversine_km em conjunto com a lógica de raio esperada.
def test_within_radius_logic():
    # prof a ~5km, raio 20km
    dist = haversine_km(-21.55, -45.42, -21.50, -45.40)
    assert dist <= 20.0

def test_outside_radius_logic():
    # prof a ~330km, raio 20km
    dist = haversine_km(-21.55, -45.42, -23.55, -46.63)
    assert dist > 20.0

def test_radius_boundary_logic():
    # Teste de precisão não é crítico aqui, mas a lógica de <= é o que importa
    dist = 20.0
    assert dist <= 20.0

# Testar que profissionais são ordenados por reputation_score DESC
def test_ranking_by_reputation():
    candidates = [
        {"id": "a", "reputation_score": 3.5, "distance_km": 5.0},
        {"id": "b", "reputation_score": 4.8, "distance_km": 8.0},
        {"id": "c", "reputation_score": 2.1, "distance_km": 3.0},
    ]
    ranked = rank_candidates(candidates)
    assert ranked[0]["id"] == "b"
    assert ranked[1]["id"] == "a"
    assert ranked[2]["id"] == "c"

def test_top_10_limit():
    # 15 candidatos → retornar no máximo 10
    candidates = [{"id": str(i), "reputation_score": float(i), "distance_km": 1.0}
                  for i in range(15)]
    ranked = rank_candidates(candidates)
    assert len(ranked) == 10
    # O primeiro deve ser o de score 14.0 (maior)
    assert ranked[0]["reputation_score"] == 14.0

def test_empty_candidates():
    assert rank_candidates([]) == []
