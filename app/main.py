from app.db.init import Database
from app.crud.user import user_crud
from app.core.logging import get_logger
from app.core.security import (
    get_password_hash,
    create_access_token,
    )
from app.core.config import settings
from app.schemas.user import UserCreate
from app.db.session import async_engine, AsyncSessionLocal
from app.models.user import GroupEnum

import asyncio


logger = get_logger(__name__)

async def main():
     # アクセストークン生成
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await create_access_token(
        data={"sub": str(id_str),
              "username": username_str},
        expires_delta=access_token_expires
    )
    
    # リフレッシュトークン生成
    refresh_token = await create_refresh_token(auth_user_id=str(db_user.id))
    
if __name__ == "__main__":
    logger.info("Starting the application")
    asyncio.run(main())
