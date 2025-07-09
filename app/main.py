from app.db.init import Database
from app.crud.user import user_crud
from app.core.logging import get_logger
from app.core.security import get_password_hash
from app.schemas.user import UserCreate
from app.db.session import async_engine, AsyncSessionLocal
from app.models.user import GroupEnum

import asyncio

logger = get_logger(__name__)

async def main():
    db = Database()
    await db.init()

    async with AsyncSessionLocal() as session:
        # 既存のユーザーをIDで取得してテスト
        existing_user = await user_crud.get_user_by_id(
            session, 
            "1ce35210-bf6d-4a21-84b1-9d3c1081eb31"  # testuser3のID
        )
        
        if existing_user:
            print(f"Found user: {existing_user.username} ({existing_user.email})")
        else:
            print("User not found")
        
        # 存在しないIDでテスト
        non_existing_user = await user_crud.get_user_by_id(
            session,
            "00000000-0000-0000-0000-000000000000"
        )
        
        if non_existing_user:
            print(f"Found user: {non_existing_user.username}")
        else:
            print("Non-existing user correctly returned None")


if __name__ == "__main__":
    logger.info("Starting the application")
    asyncio.run(main())
