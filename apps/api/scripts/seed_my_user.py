"""
Script de seed para preencher dados do usuário logado (assis.christiansales@gmail.com).

Executar:
    docker compose exec api python scripts/seed_my_user.py
"""
import asyncio
import os
import sys
from datetime import datetime, timedelta, UTC

# Adicionar raiz da app ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select, update
from app.core.database import AsyncSessionLocal
from app.models.user import User, UserRole
from app.models.professional import Professional
from app.models.category import Category
from app.models.contract import Contract
from app.models.review import Review
from app.models.request import Request
from app.models.associations import professional_categories

async def seed_my_user():
    async with AsyncSessionLocal() as session:
        # 1. Encontrar o usuário
        email = "assis.christiansales@gmail.com"
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if not user:
            print(f"❌ Usuário com e-mail {email} não encontrado no banco de dados.")
            return

        print(f"✓ Usuário encontrado: {user.id}")

        # 2. Garantir que a role é PROFESSIONAL
        if user.role != UserRole.PROFESSIONAL:
            user.role = UserRole.PROFESSIONAL
            await session.commit()
            print("✓ Role do usuário alterada para PROFESSIONAL.")

        # 3. Adicionar/Atualizar informações na tabela professionals
        result = await session.execute(select(Professional).where(Professional.user_id == user.id))
        professional = result.scalar_one_or_none()

        if not professional:
            professional = Professional(
                user_id=user.id,
                bio="Sou um especialista apaixonado pelo que faço, com mais de 10 anos de experiência em reparos complexos e atendimento ao cliente de excelência. Faço o que amo e o resultado sempre impressiona.",
                location="Centro, São Paulo",
                service_radius_km=25,
                hourly_rate_cents=15000, # R$ 150,00
                is_verified=True,
                reputation_score=4.9
            )
            session.add(professional)
            await session.commit()
            await session.refresh(professional)
            print("✓ Perfil profissional criado.")
        else:
            professional.bio = "Sou um especialista apaixonado pelo que faço, com mais de 10 anos de experiência em reparos complexos e atendimento ao cliente de excelência. Faço o que amo e o resultado sempre impressiona."
            professional.hourly_rate_cents = 15000
            professional.is_verified = True
            professional.reputation_score = 4.9
            await session.commit()
            print("✓ Perfil profissional atualizado.")

        # 4. Vincular categorias (ex: Elétrica e Hidráulica)
        result = await session.execute(select(Category).where(Category.slug.in_(['eletrica', 'hidraulica'])))
        categories = result.scalars().all()
        if categories:
            # Limpar vinculos antigos
            await session.execute(professional_categories.delete().where(professional_categories.c.professional_id == professional.id))
            # Criar novos
            for cat in categories:
                await session.execute(professional_categories.insert().values(professional_id=professional.id, category_id=cat.id))
            await session.commit()
            print(f"✓ Profissional vinculado a {len(categories)} categorias.")

        # 5. Criar cliente mock
        mock_email = "cliente.mock@example.com"
        result = await session.execute(select(User).where(User.email == mock_email))
        client = result.scalar_one_or_none()
        if not client:
            client = User(
                email=mock_email,
                name="Cliente Satisfeito",
                password_hash="mock",
                role=UserRole.CLIENT,
                is_active=True
            )
            session.add(client)
            await session.commit()
            await session.refresh(client)

        # 6. Criar requisição, contrato e review mockados para métricas
        # Contrato 1
        req1 = Request(
            client_id=client.id,
            category_id=categories[0].id if categories else None,
            title="Conserto de quadro elétrico",
            description="Troca de disjuntores e fiação parcial",
            latitude=-23.5505,
            longitude=-46.6333,
            urgency="scheduled",
            status="done"
        )
        session.add(req1)
        await session.commit()
        await session.refresh(req1)

        c1 = Contract(
            request_id=req1.id,
            professional_id=professional.id,
            client_id=client.id,
            agreed_cents=45000, # R$ 450,00
            status="completed",
            started_at=datetime.now(UTC) - timedelta(days=5),
            completed_at=datetime.now(UTC) - timedelta(days=4)
        )
        session.add(c1)
        await session.commit()
        await session.refresh(c1)

        rev1 = Review(
            contract_id=c1.id,
            reviewer_id=client.id,
            reviewee_id=user.id,
            rating=5,
            text="Trabalho excelente, muito rápido e limpo!",
            score_punctuality=1.0,
            score_quality=1.0,
            score_cleanliness=1.0,
            score_communication=1.0,
            is_authentic=True
        )
        session.add(rev1)

        # Contrato 2
        req2 = Request(
            client_id=client.id,
            category_id=categories[1].id if len(categories) > 1 else None,
            title="Instalação de torneira",
            description="Instalação de torneira monocomando na cozinha",
            latitude=-23.5505,
            longitude=-46.6333,
            urgency="flexible",
            status="done"
        )
        session.add(req2)
        await session.commit()
        await session.refresh(req2)

        c2 = Contract(
            request_id=req2.id,
            professional_id=professional.id,
            client_id=client.id,
            agreed_cents=20000, # R$ 200,00
            status="completed",
            started_at=datetime.now(UTC) - timedelta(days=2),
            completed_at=datetime.now(UTC) - timedelta(days=1)
        )
        session.add(c2)
        await session.commit()
        await session.refresh(c2)

        rev2 = Review(
            contract_id=c2.id,
            reviewer_id=client.id,
            reviewee_id=user.id,
            rating=4,
            text="Ficou bom, só demorou um pouco para chegar.",
            score_punctuality=0.6,
            score_quality=1.0,
            score_cleanliness=0.8,
            score_communication=1.0,
            is_authentic=True
        )
        session.add(rev2)
        
        await session.commit()
        print("✓ Contratos e Avaliações de teste criados (Ganhos Totais: R$ 650,00 | Avaliações: 2).")
        
        print("\n✅ Seed finalizado com sucesso! Seu usuário agora tem dados de profissional.")

if __name__ == "__main__":
    asyncio.run(seed_my_user())
