"""テストデータクリーンアップスクリプト"""
import asyncio
from sqlalchemy import text
from app.db.session import AsyncSessionLocal

async def cleanup_test_data():
    """テストデータをクリーンアップする"""
    async with AsyncSessionLocal() as session:
        try:
            # パフォーマンステストデータを削除
            delete_query = text("""
                DELETE FROM users 
                WHERE username LIKE 'perftest%'
                OR username LIKE 'edgetest%'
                OR username LIKE 'testfilter%'
            """)
            
            result = await session.execute(delete_query)
            await session.commit()
            
            print(f"Deleted {result.rowcount} test users")
            
            # 残りのユーザー数を確認
            count_query = text("SELECT COUNT(*) FROM users")
            result = await session.execute(count_query)
            remaining_count = result.scalar()
            
            print(f"Remaining users in database: {remaining_count}")
            
        except Exception as e:
            await session.rollback()
            print(f"Error during cleanup: {e}")

if __name__ == "__main__":
    asyncio.run(cleanup_test_data())