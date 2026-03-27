"""
Script de seed das 16 categorias iniciais do ServiçoJá.

Executar:
    docker compose exec api python scripts/seed_categories.py

Referência: openspec/changes/service-marketplace-platform/specs/categories-seed/spec.md
"""
import asyncio
import os
import sys

# Adicionar raiz da app ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.category import Category

CATEGORIES = [
    {"name": "Hidráulica",      "slug": "hidraulica",      "color": "#2e7bc4", "sort_order": 1},
    {"name": "Elétrica",        "slug": "eletrica",        "color": "#d4a00a", "sort_order": 2},
    {"name": "Gás",             "slug": "gas",             "color": "#e06820", "sort_order": 3},
    {"name": "Construção",      "slug": "construcao",      "color": "#b04020", "sort_order": 4},
    {"name": "Jardinagem",      "slug": "jardinagem",      "color": "#2a8c50", "sort_order": 5},
    {"name": "Limpeza",         "slug": "limpeza",         "color": "#18a0a0", "sort_order": 6},
    {"name": "Pintura",         "slug": "pintura",         "color": "#9050c0", "sort_order": 7},
    {"name": "Marcenaria",      "slug": "marcenaria",      "color": "#8a5c28", "sort_order": 8},
    {"name": "Ar-condicionado", "slug": "ar-condicionado", "color": "#4898d8", "sort_order": 9},
    {"name": "Segurança",       "slug": "seguranca",       "color": "#384880", "sort_order": 10},
    {"name": "Tecnologia",      "slug": "tecnologia",      "color": "#20a870", "sort_order": 11},
    {"name": "Reformas",        "slug": "reformas",        "color": "#c06840", "sort_order": 12},
    {"name": "Saúde/Beleza",    "slug": "saude-beleza",    "color": "#d04080", "sort_order": 13},
    {"name": "Jurídico",        "slug": "juridico",        "color": "#485870", "sort_order": 14},
    {"name": "Educação",        "slug": "educacao",        "color": "#e08820", "sort_order": 15},
    {"name": "Pets",            "slug": "pets",            "color": "#d85020", "sort_order": 16},
]


async def seed_categories() -> None:
    """Inserir categorias iniciais, pulando as que já existem."""
    async with AsyncSessionLocal() as session:
        created = 0
        skipped = 0

        for cat_data in CATEGORIES:
            stmt = select(Category).where(Category.slug == cat_data["slug"])
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()

            if not existing:
                session.add(Category(**cat_data))
                print(f"  ✓ Criada:    {cat_data['name']} ({cat_data['color']})")
                created += 1
            else:
                print(f"  ⊘ Já existe: {cat_data['name']}")
                skipped += 1

        await session.commit()

    print(f"\n✅ Seed concluído — {created} criadas · {skipped} já existiam")


if __name__ == "__main__":
    asyncio.run(seed_categories())
