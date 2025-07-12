from app.db.session import AsyncSessionLocal
from sqlalchemy.sql import text
import asyncio

async def fix_enum():
    async with AsyncSessionLocal() as session:
        # Drop the existing table and enum
        await session.execute(text("DROP TABLE IF EXISTS users CASCADE;"))
        await session.execute(text("DROP TYPE IF EXISTS groupenum CASCADE;"))
        
        # Create ENUM type with the same names as in Python
        await session.execute(text("""
            CREATE TYPE groupenum AS ENUM ('CSC_1', 'CSC_2', 'CSC_N', 'HHD');
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
        print("Fixed ENUM and recreated users table")

if __name__ == "__main__":
    asyncio.run(fix_enum())