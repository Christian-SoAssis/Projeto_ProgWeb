import asyncio
import os
import sys
import random
from uuid import uuid4
from datetime import datetime, timedelta

# Adicionar raiz da app ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.user import User, UserRole
from app.models.professional import Professional
from app.models.category import Category
from app.models.request import Request
from app.models.bid import Bid
from app.core.security import hash_password

async def seed_demo_flow():
    async with AsyncSessionLocal() as session:
        # 1. Ponto central e dados base
        lat_base, lng_base = -21.5565, -45.4340
        email_client = "cliente_teste@example.com"
        
        # 2. Garantir Cliente de Teste
        stmt = select(User).where(User.email == email_client)
        result = await session.execute(stmt)
        client = result.scalar_one_or_none()
        
        if not client:
            client = User(
                name="Cliente de Teste",
                email=email_client,
                password_hash=hash_password("password123"),
                role=UserRole.CLIENT,
                is_active=True
            )
            session.add(client)
            await session.flush()
            print("  ✓ Cliente de Teste criado.")
        else:
            print("  ⊘ Cliente de Teste já existe.")

        # 3. Buscar Categorias e Profissionais disponíveis
        cats_stmt = select(Category)
        profs_stmt = select(Professional)
        
        result_cats = await session.execute(cats_stmt)
        result_profs = await session.execute(profs_stmt)
        
        categories = result_cats.scalars().all()
        professionals = result_profs.scalars().all()
        
        if not categories or not professionals:
            print("❌ Erro: Preciso de categorias e profissionais para rodar o flow. Rode os outros seeds primeiro.")
            return

        DEMO_REQUESTS = [
            {"title": "Goteira persistente na sala", "urgency": "immediate", "budget": 20000},
            {"title": "Trocar fiação do chuveiro", "urgency": "immediate", "budget": 15000},
            {"title": "Limpeza de jardim frontal", "urgency": "scheduled", "budget": 30000},
            {"title": "Pintura de quarto de bebê", "urgency": "flexible", "budget": 60000},
        ]

        for req_data in DEMO_REQUESTS:
            # Selecionar categoria aleatória
            cat = random.choice(categories)
            
            # Verificar se pedido com esse título já existe para este cliente
            stmt = select(Request).where(Request.client_id == client.id, Request.title == req_data["title"])
            res = await session.execute(stmt)
            if res.scalar_one_or_none():
                print(f"  ⊘ Pedido já existe: {req_data['title']}")
                continue

            # Criar Pedido
            # No PostGIS usamos WKT para o Point
            point_wkt = f"POINT({lng_base} {lat_base})"
            
            request = Request(
                client_id=client.id,
                category_id=cat.id,
                title=req_data["title"],
                description=f"Pedido de teste criado para verificar o design do dashboard. Categoria: {cat.name}.",
                location=point_wkt,
                urgency=req_data["urgency"],
                budget_cents=req_data["budget"],
                status="open"
            )
            session.add(request)
            await session.flush()
            print(f"  ✓ Pedido criado: {req_data['title']}")

            # Criar 1 a 3 bids para este pedido
            possible_profs = [p for p in professionals if cat in p.categories] or professionals
            selected_profs = random.sample(possible_profs, min(len(possible_profs), random.randint(1, 3)))
            
            for prof in selected_profs:
                bid = Bid(
                    request_id=request.id,
                    professional_id=prof.id,
                    price_cents=int(req_data["budget"] * random.uniform(0.8, 1.2)),
                    estimated_hours=random.randint(2, 24),
                    message="Olá, tenho experiência com esse tipo de serviço e disponibilidade imediata.",
                    status="pending"
                )
                session.add(bid)
                # Mudar status do pedido para 'matched' se houver bids
                request.status = "matched"
            
            print(f"    - {len(selected_profs)} propostas geradas.")

        await session.commit()
        print(f"\n✅ Fluxo de demonstração concluído!")

if __name__ == "__main__":
    asyncio.run(seed_demo_flow())
