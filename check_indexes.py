"""インデックス確認スクリプト"""
import asyncio
from sqlalchemy import text
from app.db.session import AsyncSessionLocal

async def check_indexes():
    """インデックス状況を確認する"""
    async with AsyncSessionLocal() as session:
        # ユーザーテーブルのインデックス確認
        query = text("""
        SELECT indexname, indexdef 
        FROM pg_indexes 
        WHERE tablename = 'users'
        ORDER BY indexname
        """)
        result = await session.execute(query)
        
        print("=== Users テーブルのインデックス一覧 ===")
        for row in result:
            print(f"インデックス名: {row.indexname}")
            print(f"定義: {row.indexdef}")
            print()

if __name__ == "__main__":
    asyncio.run(check_indexes())