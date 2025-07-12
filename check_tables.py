from app.db.session import AsyncSessionLocal
from sqlalchemy.sql import text
import asyncio

async def check_tables():
    async with AsyncSessionLocal() as session:
        result = await session.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = current_schema()"))
        tables = [row[0] for row in result]
        print("Existing tables:", tables)

if __name__ == "__main__":
    asyncio.run(check_tables())