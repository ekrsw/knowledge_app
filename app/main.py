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

    user_obj = UserCreate(
        username="testuser",
        email="test2@email.com",
        password="password",
        group=GroupEnum.CSC_2
    )
    
    async with AsyncSessionLocal() as session:
        await user_crud.create_user(session, obj_in=user_obj)
        await session.commit()


if __name__ == "__main__":
    logger.info("Starting the application")
    asyncio.run(main())