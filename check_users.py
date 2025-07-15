import asyncio
from app.db.session import AsyncSessionLocal
from app.models.user import User
from sqlalchemy import select

async def check_users():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        
        print("Users in database:")
        print("-" * 80)
        for user in users:
            print(f"Username: {user.username}")
            print(f"Email: {user.email}")
            print(f"ID: {user.id}")
            print(f"Created: {user.created_at}")
            print("-" * 80)

if __name__ == "__main__":
    asyncio.run(check_users())