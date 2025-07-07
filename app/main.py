from app.db.init import Database
from app.crud.user import user_crud
from app.core.logging import get_logger
from app.core.security import get_password_hash
from app.schemas.user import UserCreate
from app.db.session import get_async_session
from fastapi import Depends
import asyncio

logger = get_logger(__name__)

async def main():
    db = Database()
    await db.init()

    user_obj = UserCreate(
        username="testuser",
        email="test@email.com",
        password="password"
    )
    
    await user_crud.create_user(Depends(get_async_session), obj_in=user_obj)


if __name__ == "__main__":
    logger.info("Starting the application")
    asyncio.run(main())