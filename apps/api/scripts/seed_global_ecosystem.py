"""
Seed global de ecossistema para o perfil do usuário logado (assis.christiansales@gmail.com).

Gera:
- Contas de clientes (joao, maria, carlos) com senha 'senha123'
- Propostas abertas (Open Requests) na região
- Lances pendentes (Pending Bids) do profissional
- Contratos em andamento (In Progress Contracts)
- Contratos concluídos e avaliações ricas

Executar:
    docker compose exec api python scripts/seed_global_ecosystem.py
"""
import asyncio
import os
import sys
from datetime import datetime, timedelta, UTC

# Adicionar raiz da app ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select, update
from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.models.user import User, UserRole
from app.models.professional import Professional
from app.models.category import Category
from app.models.contract import Contract
from app.models.review import Review
from app.models.request import Request
from app.models.bid import Bid
from app.models.associations import professional_categories

async def seed_global_ecosystem():
    async with AsyncSessionLocal() as session:
        # ==========================================
        # 1. Configurar Profissional
        # ==========================================
        email = "assis.christiansales@gmail.com"
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if not user:
            print(f"❌ Usuário principal ({email}) não encontrado.")
            return

        print(f"✓ Usuário principal encontrado: {user.name}")

        if user.role != UserRole.PROFESSIONAL:
            user.role = UserRole.PROFESSIONAL
            await session.commit()

        result = await session.execute(select(Professional).where(Professional.user_id == user.id))
        professional = result.scalar_one_or_none()

        if not professional:
            professional = Professional(
                user_id=user.id,
                bio="Especialista em manutenções complexas com mais de 10 anos de experiência. Foco na excelência, limpeza e na rápida resolução dos problemas.",
                latitude=-23.5505,
                longitude=-46.6333,
                service_radius_km=25,
                hourly_rate_cents=18000, # R$ 180,00
                is_verified=True,
                reputation_score=4.9
            )
            session.add(professional)
            await session.commit()
            await session.refresh(professional)
        else:
            professional.is_verified = True
            professional.hourly_rate_cents = 18000
            await session.commit()
            
        print("✓ Perfil do profissional configurado.")

        # Garantir categorias
        result = await session.execute(select(Category).where(Category.slug.in_(['eletrica', 'hidraulica', 'reformas'])))
        categories = result.scalars().all()
        if categories:
            await session.execute(professional_categories.delete().where(professional_categories.c.professional_id == professional.id))
            for cat in categories:
                await session.execute(professional_categories.insert().values(professional_id=professional.id, category_id=cat.id))
            await session.commit()

        # ==========================================
        # 2. Criar Clientes de Teste
        # ==========================================
        clients_data = [
            ("joao.cliente@test.com", "João Silva"),
            ("maria.cliente@test.com", "Maria Oliveira"),
            ("carlos.cliente@test.com", "Carlos Santos")
        ]
        
        clients = []
        hashed_pwd = hash_password("senha123")
        
        for c_email, c_name in clients_data:
            result = await session.execute(select(User).where(User.email == c_email))
            client = result.scalar_one_or_none()
            if not client:
                client = User(
                    email=c_email,
                    name=c_name,
                    password_hash=hashed_pwd,
                    role=UserRole.CLIENT,
                    is_active=True
                )
                session.add(client)
            else:
                client.password_hash = hashed_pwd
            clients.append(client)
        
        await session.commit()
        for c in clients:
            await session.refresh(c)
        print(f"✓ Clientes de teste configurados ({len(clients)} contas com senha 'senha123').")

        # ==========================================
        # 3. Oportunidades Abertas (Requests)
        # ==========================================
        cat_eletrica = next((c for c in categories if c.slug == 'eletrica'), None)
        cat_hidraulica = next((c for c in categories if c.slug == 'hidraulica'), None)
        cat_reforma = next((c for c in categories if c.slug == 'reformas'), None)
        
        open_reqs_data = [
            (clients[0], cat_eletrica, "Troca de fiação no apartamento", "Preciso trocar a fiação antiga de 3 cômodos.", "flexible", 120000),
            (clients[1], cat_hidraulica, "Vazamento forte no banheiro", "O cano da pia estourou e está alagando tudo!", "immediate", 30000),
            (clients[2], cat_eletrica, "Instalação de ar-condicionado", "Instalar ar split 12000 btus no quarto.", "scheduled", 50000)
        ]
        
        for client, cat, title, desc, urg, budget in open_reqs_data:
            if not cat: continue
            req = Request(
                client_id=client.id,
                category_id=cat.id,
                title=title,
                description=desc,
                latitude=-23.5510,
                longitude=-46.6340,
                urgency=urg,
                budget_cents=budget,
                status="open"
            )
            session.add(req)
        await session.commit()
        print("✓ Oportunidades abertas geradas (Requests open).")

        # ==========================================
        # 4. Propostas Enviadas (Bids pendentes)
        # ==========================================
        # Criar uns requests para o prof dar bid
        bid_req1 = Request(
            client_id=clients[0].id,
            category_id=cat_reforma.id if cat_reforma else cat_eletrica.id,
            title="Pintura e reparos gerais",
            description="Reparos nas paredes e pintura.",
            latitude=-23.5500,
            longitude=-46.6300,
            urgency="flexible",
            status="open"
        )
        session.add(bid_req1)
        await session.commit()
        await session.refresh(bid_req1)
        
        bid1 = Bid(
            request_id=bid_req1.id,
            professional_id=professional.id,
            price_cents=150000,
            estimated_hours=16,
            message="Tenho muita experiência com isso. Posso começar amanhã.",
            status="pending"
        )
        session.add(bid1)
        await session.commit()
        print("✓ Lances (bids) pendentes enviados.")

        # ==========================================
        # 5. Trabalhos em Andamento (Contracts in_progress)
        # ==========================================
        prog_req = Request(
            client_id=clients[1].id,
            category_id=cat_eletrica.id if cat_eletrica else None,
            title="Revisão elétrica completa",
            description="Revisar toda a casa de 2 quartos.",
            latitude=-23.5600,
            longitude=-46.6400,
            urgency="scheduled",
            status="in_progress"
        )
        session.add(prog_req)
        await session.commit()
        await session.refresh(prog_req)
        
        prog_contract = Contract(
            request_id=prog_req.id,
            professional_id=professional.id,
            client_id=clients[1].id,
            agreed_cents=80000,
            status="active",
            started_at=datetime.now(UTC) - timedelta(days=1)
        )
        session.add(prog_contract)
        await session.commit()
        print("✓ Trabalhos em andamento gerados (in_progress).")

        # ==========================================
        # 6. Histórico e Métricas (Contracts completed + Reviews)
        # ==========================================
        completed_data = [
            (clients[0], cat_hidraulica, "Desentupimento de pia", 25000, 5, "Ótimo trabalho, super educado e não sujou nada.", 1.0, 1.0, 1.0, 1.0, 4),
            (clients[2], cat_eletrica, "Instalação de luminárias", 35000, 4, "Instalou tudo certo, mas atrasou um pouquinho.", 0.6, 1.0, 1.0, 0.8, 2),
            (clients[1], cat_reforma, "Conserto de gesso", 60000, 5, "Trabalho impecável, muito caprichoso.", 1.0, 1.0, 1.0, 1.0, 10),
            (clients[0], cat_eletrica, "Troca de chuveiro", 15000, 5, "Rápido e eficiente, resolveu no mesmo dia.", 1.0, 1.0, 1.0, 1.0, 15)
        ]
        
        for client, cat, title, price, rating, text, sp, sq, sc, scom, days_ago in completed_data:
            if not cat: continue
            creq = Request(
                client_id=client.id,
                category_id=cat.id,
                title=title,
                latitude=-23.5505,
                longitude=-46.6333,
                urgency="flexible",
                status="done"
            )
            session.add(creq)
            await session.commit()
            await session.refresh(creq)
            
            ccont = Contract(
                request_id=creq.id,
                professional_id=professional.id,
                client_id=client.id,
                agreed_cents=price,
                status="completed",
                started_at=datetime.now(UTC) - timedelta(days=days_ago),
                completed_at=datetime.now(UTC) - timedelta(days=days_ago-1)
            )
            session.add(ccont)
            await session.commit()
            await session.refresh(ccont)
            
            crev = Review(
                contract_id=ccont.id,
                reviewer_id=client.id,
                reviewee_id=user.id,
                rating=rating,
                text=text,
                score_punctuality=sp,
                score_quality=sq,
                score_cleanliness=sc,
                score_communication=scom,
                is_authentic=True,
                created_at=datetime.now(UTC) - timedelta(days=days_ago-1)
            )
            session.add(crev)
        
        await session.commit()
        print("✓ Histórico de contratos concluídos e avaliações inseridos.")
        print("\n✅ SEED GLOBAL DE ECOSSISTEMA FINALIZADO COM SUCESSO!")

if __name__ == "__main__":
    asyncio.run(seed_global_ecosystem())
