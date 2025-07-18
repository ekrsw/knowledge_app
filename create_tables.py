from app.db.session import async_engine
from app.db.base import Base
import asyncio

async def create_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("Tables created successfully")

if __name__ == "__main__":
    asyncio.run(create_tables())