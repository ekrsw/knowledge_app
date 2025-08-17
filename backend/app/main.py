"""
FastAPI application entry point for Knowledge Revision System
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.core.config import settings

app = FastAPI(
    title="KSAP - Knowledge System Approval Platform",
    description="""## ナレッジシステム承認プラットフォーム API

KSAPは、ナレッジの修正提案と承認を効率的に管理する包括的なシステムです。

### 主要機能
- **修正案管理**: ナレッジの修正提案を作成・編集・提出し、進捗を追跡
- **承認ワークフロー**: ロールベースのアクセス制御による構造化された承認プロセス
- **差分分析**: 高度な変更検出と影響度評価機能
- **通知システム**: リアルタイム通知とコミュニケーション機能
- **分析・レポート**: 包括的なメトリクスとパフォーマンス分析

### ユーザー権限
- **一般ユーザー**: 自分の修正提案を作成・管理
- **承認者**: 担当領域の提案をレビューし、承認・却下の判断
- **管理者**: ユーザー管理やシステム設定を含む全機能へのアクセス

### 認証について
公開エンドポイント以外の全てのAPIは、JWT Bearer トークン認証が必要です。

**認証ヘッダーの形式:**
```
Authorization: Bearer <JWT アクセストークン>
```

### API構造
- **ベースURL**: `/api/v1`
- **認証方式**: JWT Bearer トークン
- **レスポンス形式**: JSON
- **エラーハンドリング**: 標準HTTPステータスコードと詳細なエラーメッセージ

### 主要エンドポイント
- `/auth/login` - ユーザー認証
- `/proposals/` - 修正提案の管理
- `/approvals/` - 承認ワークフロー
- `/diffs/` - 変更分析
- `/system/health` - ヘルスチェック

### サポート
技術的なサポートや機能要望については、開発チームまでお問い合わせください。
""",
    version="0.1.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json" if settings.ENVIRONMENT != "production" else None,
    contact={
        "name": "KSAP Development Team",
        "email": "dev-team@company.com",
    },
    license_info={
        "name": "Proprietary License",
        "url": "https://company.com/license",
    },
    # SwaggerUI設定でMarkdownレンダリングを改善
    swagger_ui_parameters={
        "defaultModelsExpandDepth": 2,
        "defaultModelExpandDepth": 2,
        "displayOperationId": False,
        "displayRequestDuration": True,
        "docExpansion": "list",
        "filter": True,
        "showExtensions": True,
        "showCommonExtensions": True,
        "syntaxHighlight.theme": "agate",
    },
)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    """Root endpoint - API Welcome"""
    return {
        "message": "Welcome to KSAP - Knowledge System Approval Platform",
        "version": "0.1.0",
        "status": "operational",
        "documentation": "/docs",
        "api_base": "/api/v1",
        "health_check": "/health"
    }

@app.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": "2025-01-30T00:00:00Z",
        "version": "0.1.0"
    }