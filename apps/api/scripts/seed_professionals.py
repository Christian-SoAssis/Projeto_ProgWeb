import asyncio
import os
import sys
import random
from uuid import uuid4

# Adicionar raiz da app ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.user import User, UserRole
from app.models.professional import Professional
from app.models.category import Category
from app.core.security import hash_password

PROFESSIONALS_DATA = [
    {"name": "Carlos Silva", "bio": "Encanador experiente há 15 anos. Especialista em vazamentos e reparos hidráulicos urgentes.", "category": "hidraulica", "rate": 8000},
    {"name": "Ana Souza", "bio": "Eletricista certificada. Instalação de quadros, tomadas e ventiladores com segurança.", "category": "eletrica", "rate": 9500},
    {"name": "Ricardo Manutenções", "bio": "Marido de aluguel para pequenos reparos, pintura e montagem de móveis.", "category": "reformas", "rate": 6000},
    {"name": "Beatriz Jardinagem", "bio": "Paisagismo e manutenção de jardins residenciais e comerciais.", "category": "jardinagem", "rate": 7500},
    {"name": "Marcos Tech", "bio": "Suporte técnico de TI, redes e configuração de smart homes.", "category": "tecnologia", "rate": 12000},
    {"name": "Limpeza Brilho", "bio": "Serviços de limpeza pós-obra e faxinas pesadas com equipe especializada.", "category": "limpeza", "rate": 5000},
    {"name": "Juliana Pinturas", "bio": "Pintura residencial interna e externa com acabamento premium.", "category": "pintura", "rate": 8500},
    {"name": "Fernando Gás", "bio": "Instalação e conversão de fogões e aquecedores a gás.", "category": "gas", "rate": 11000},
]

async def seed_professionals():
    async with AsyncSessionLocal() as session:
        # Ponto central (onde o usuário está testando)
        lat_base, lng_base = -21.5565, -45.4340
        
        # Buscar categorias
        stmt = select(Category)
        result = await session.execute(stmt)
        categories_map = {cat.slug: cat for cat in result.scalars().all()}
        
        if not categories_map:
            print("❌ Erro: Nenhuma categoria encontrada. Rode seed_categories.py primeiro.")
            return

        created_count = 0
        for data in PROFESSIONALS_DATA:
            email = f"prof_{data['category']}@example.com"
            
            # Verificar se já existe
            stmt = select(User).where(User.email == email)
            result = await session.execute(stmt)
            if result.scalar_one_or_none():
                print(f"  ⊘ Profissional já existe: {data['name']}")
                continue

            # Criar Usuário
            user = User(
                name=data["name"],
                email=email,
                password_hash=hash_password("password123"),
                role=UserRole.PROFESSIONAL,
                is_active=True
            )
            session.add(user)
            await session.flush() # Para pegar o ID

            # Criar Perfil Profissional
            # Deslocamento aleatório de até ~5km
            lat = lat_base + (random.uniform(-0.04, 0.04))
            lng = lng_base + (random.uniform(-0.04, 0.04))
            
            prof = Professional(
                user_id=user.id,
                bio=data["bio"],
                latitude=lat,
                longitude=lng,
                service_radius_km=30.0,
                hourly_rate_cents=data["rate"],
                reputation_score=random.uniform(4.0, 5.0),
                is_verified=True
            )
            
            # Adicionar categoria
            cat = categories_map.get(data["category"])
            if cat:
                prof.categories.append(cat)
            
            session.add(prof)
            print(f"  ✓ Criado: {data['name']} ({data['category']})")
            created_count += 1

        await session.commit()
        print(f"\n✅ Seed de Profissionais concluído: {created_count} criados.")

if __name__ == "__main__":
    asyncio.run(seed_professionals())
