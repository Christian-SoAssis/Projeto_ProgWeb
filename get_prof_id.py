import asyncio
from app.core.database import AsyncSessionLocal
from app.models.professional import Professional
from sqlalchemy import select

async def get_id():
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(Professional.id).limit(1))
        print(res.scalar())

if __name__ == "__main__":
    asyncio.run(get_id())
