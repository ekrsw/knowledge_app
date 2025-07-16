"""ユーザー数確認スクリプト"""
import asyncio
from sqlalchemy import text
from app.db.session import AsyncSessionLocal

async def check_user_count():
    """ユーザー数を確認する"""
    async with AsyncSessionLocal() as session:
        # 総ユーザー数を確認
        query = text("SELECT COUNT(*) FROM users")
        result = await session.execute(query)
        total_count = result.scalar()
        
        print(f"Total users in database: {total_count}")
        
        # テストデータの確認
        test_patterns = [
            "test%",
            "edgetest%",
            "perftest%",
            "pag%"
        ]
        
        for pattern in test_patterns:
            query = text("SELECT COUNT(*) FROM users WHERE username LIKE :pattern")
            result = await session.execute(query, {"pattern": pattern})
            count = result.scalar()
            print(f"Users matching '{pattern}': {count}")

if __name__ == "__main__":
    asyncio.run(check_user_count())