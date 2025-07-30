"""
Test database and Redis connections
"""
import asyncio
import asyncpg
import redis
from app.core.config import settings


async def test_postgres_connection():
    """Test PostgreSQL connection"""
    try:
        conn = await asyncpg.connect(settings.DATABASE_URL)
        version = await conn.fetchval('SELECT version()')
        print(f"✅ PostgreSQL connection successful")
        print(f"   Version: {version}")
        await conn.close()
        return True
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        return False


async def test_redis_connection():
    """Test Redis connection"""
    try:
        r = redis.from_url(settings.REDIS_URL)
        r.ping()
        info = r.info()
        print(f"✅ Redis connection successful")
        print(f"   Version: {info.get('redis_version', 'Unknown')}")
        r.close()
        return True
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return False


async def main():
    """Main test function"""
    print("Testing database connections...")
    
    postgres_ok = await test_postgres_connection()
    redis_ok = await test_redis_connection()
    
    if postgres_ok and redis_ok:
        print("\n🎉 All connections successful!")
        return 0
    else:
        print("\n💥 Some connections failed!")
        return 1


if __name__ == "__main__":
    import sys
    sys.path.append("../backend")
    exit_code = asyncio.run(main())
    exit(exit_code)