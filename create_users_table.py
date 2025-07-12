from app.db.session import AsyncSessionLocal
from sqlalchemy.sql import text
import asyncio

async def create_users_table():
    async with AsyncSessionLocal() as session:
        # Create ENUM type
        await session.execute(text("""
            CREATE TYPE groupenum AS ENUM ('東京CSC第一グループ', '東京CSC第二グループ', '長岡CSCグループ', 'HHDグループ');
        """))
        
        # Create users table
        await session.execute(text("""
            CREATE TABLE users (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                username VARCHAR NOT NULL UNIQUE,
                email VARCHAR NOT NULL UNIQUE,
                full_name VARCHAR,
                ctstage_name VARCHAR,
                sweet_name VARCHAR,
                "group" groupenum NOT NULL,
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                is_admin BOOLEAN NOT NULL DEFAULT FALSE,
                is_sv BOOLEAN NOT NULL DEFAULT FALSE,
                hashed_password VARCHAR NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
            );
        """))
        
        # Create indexes
        await session.execute(text("CREATE INDEX ix_users_username ON users (username);"))
        await session.execute(text("CREATE INDEX ix_users_email ON users (email);"))
        await session.execute(text("CREATE INDEX ix_users_full_name ON users (full_name);"))
        await session.execute(text("CREATE INDEX ix_users_id ON users (id);"))
        
        await session.commit()
        print("Users table created successfully")

if __name__ == "__main__":
    asyncio.run(create_users_table())