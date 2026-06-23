"""
Script para criar dois usuários fictícios de teste (cliente e profissional).

Executar:
    docker compose exec api python scripts/create_test_users.py
"""
import asyncio
import os
import sys

# Adicionar raiz da app ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.user import User, UserRole
from app.models.professional import Professional
from app.core.security import hash_password

async def create_users():
    async with AsyncSessionLocal() as session:
        # 1. Usuário Cliente
        client_email = "cliente.teste@ficticio.com"
        result_client = await session.execute(select(User).where(User.email == client_email))
        client = result_client.scalar_one_or_none()
        
        if not client:
            client = User(
                name="Cliente Ficticio",
                email=client_email,
                password_hash=hash_password("senha123"),
                role=UserRole.CLIENT,
                is_active=True
            )
            session.add(client)
            await session.flush()
            print(f"✅ Cliente de teste criado com sucesso!")
            print(f"   Email: {client_email}")
            print(f"   Senha: senha123")
        else:
            print(f"ℹ️ Cliente {client_email} já existe.")

        # 2. Usuário Profissional
        prof_email = "profissional.teste@ficticio.com"
        result_prof = await session.execute(select(User).where(User.email == prof_email))
        prof_user = result_prof.scalar_one_or_none()
        
        if not prof_user:
            prof_user = User(
                name="Profissional Ficticio",
                email=prof_email,
                password_hash=hash_password("senha123"),
                role=UserRole.PROFESSIONAL,
                is_active=True
            )
            session.add(prof_user)
            await session.flush()
            
            # Criar perfil na tabela professionals
            professional = Professional(
                user_id=prof_user.id,
                bio="Sou um eletricista/encanador profissional de teste. Atendimento rápido e de qualidade.",
                latitude=-21.5565,
                longitude=-45.4340,
                service_radius_km=30.0,
                hourly_rate_cents=9000, # R$ 90,00/h
                is_verified=True,
                reputation_score=4.8
            )
            session.add(professional)
            await session.flush()
            
            print(f"✅ Profissional de teste criado com sucesso!")
            print(f"   Email: {prof_email}")
            print(f"   Senha: senha123")
        else:
            print(f"ℹ️ Profissional {prof_email} já existe.")
            
        await session.commit()
        print("\n🎉 Usuários prontos para uso em testes!")

if __name__ == "__main__":
    asyncio.run(create_users())
