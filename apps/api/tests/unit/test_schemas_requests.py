import pytest
from pydantic import ValidationError
from uuid import uuid4
from app.schemas.v1.requests import RequestCreate, RequestUpdate, RequestResponse
from app.schemas.v1.categories import CategoryCreate, CategoryResponse

# --------------------------------------------------------------------------
# 3.T3a — RequestCreate (Inputs Inválidos)
# --------------------------------------------------------------------------

def test_request_create_validations():
    category_id = uuid4()
    
    # Sucessos
    valid_data = {
        "title": "Torneira vazando",
        "category_id": category_id,
        "urgency": "immediate",
        "latitude": -23.5505,
        "longitude": -46.6333,
        "budget_cents": 10000
    }
    obj = RequestCreate(**valid_data)
    assert obj.title == "Torneira vazando"
    
    # Sucesso - budget_cents opcional
    valid_no_budget = valid_data.copy()
    valid_no_budget.pop("budget_cents")
    obj2 = RequestCreate(**valid_no_budget)
    assert obj2.budget_cents is None
    
    # Falhas
    invalid_cases = [
        {"title": ""}, # Empty
        {"title": "ab"}, # < 5
        {"urgency": "urgent"}, # Pattern mismatch
        {"urgency": "high"},   # Pattern mismatch
        {"budget_cents": 0},   # gt 0
        {"budget_cents": -1},  # gt 0
        {"latitude": 90.1},    # le 90
        {"latitude": -90.1},   # ge -90
        {"longitude": 180.1},  # le 180
        {"category_id": "not-a-uuid"},
    ]
    
    for case in invalid_cases:
        test_data = valid_data.copy()
        test_data.update(case)
        with pytest.raises(ValidationError):
            RequestCreate(**test_data)

# --------------------------------------------------------------------------
# 3.T3b — RequestUpdate (Campos Opcionais)
# --------------------------------------------------------------------------

def test_request_update_validations():
    # Sucesso - Tudo vazio
    obj = RequestUpdate()
    assert obj.title is None
    
    # Falhas se presente mas inválido
    with pytest.raises(ValidationError):
        RequestUpdate(title="ab")
        
    with pytest.raises(ValidationError):
        RequestUpdate(budget_cents=-50)
        
    # Sucesso - budget_cents=None (válido se marcado como Optional)
    obj2 = RequestUpdate(budget_cents=None)
    assert obj2.budget_cents is None

# --------------------------------------------------------------------------
# 3.T3c — CategoryCreate
# --------------------------------------------------------------------------

def test_category_create_validations():
    # Sucesso
    valid_cat = {
        "name": "Manutenção Hidráulica",
        "slug": "manutencao-hidraulica",
        "color": "#123456",
        "sort_order": 1
    }
    obj = CategoryCreate(**valid_cat)
    assert obj.slug == "manutencao-hidraulica"
    
    # Falhas
    invalid_cats = [
        {"name": ""},
        {"slug": "Minha Categoria"}, # Espaço e Uppercase
        {"slug": "minha_categoria"}, # Underscore não permitido pelo regex ^[a-z0-9-]+$
        {"color": "red"}, # Pattern mismatch (#RRGGBB)
        {"sort_order": -1}, # ge 0
    ]
    
    for case in invalid_cats:
        test_data = valid_cat.copy()
        test_data.update(case)
        with pytest.raises(ValidationError):
            CategoryCreate(**test_data)

# --------------------------------------------------------------------------
# 3.T3d — from_attributes (Model Validation)
# --------------------------------------------------------------------------

class MockORM:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

def test_request_response_from_attributes():
    from datetime import datetime
    now = datetime.now()
    req_id = uuid4()
    client_id = uuid4()
    cat_id = uuid4()
    
    mock_req = MockORM(
        id=req_id,
        client_id=client_id,
        category_id=cat_id,
        title="Reparo na fiação",
        description="Curto circuito na sala",
        urgency="immediate",
        budget_cents=15000,
        latitude=-23.0,
        longitude=-45.0,
        status="open",
        ai_complexity="simple",
        ai_urgency="low",
        ai_specialties=["Troca de disjuntor"],
        created_at=now,
        updated_at=now,
        images=[]
    )
    
    response = RequestResponse.model_validate(mock_req)
    assert response.id == req_id
    assert response.title == "Reparo na fiação"
    assert response.ai_specialties == ["Troca de disjuntor"]

def test_category_response_from_attributes():
    cat_id = uuid4()
    mock_cat = MockORM(
        id=cat_id,
        name="Elétrica",
        slug="eletrica",
        color="#FF0000",
        parent_id=None,
        sort_order=0,
        is_active=True,
        children=[]
    )
    
    response = CategoryResponse.model_validate(mock_cat)
    assert response.id == cat_id
    assert response.name == "Elétrica"
