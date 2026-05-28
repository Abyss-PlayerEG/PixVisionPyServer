"""
FastAPI 主应用
"""
import sys
from pathlib import Path

# 将项目根目录加入 sys.path，确保 app 包可被正确导入
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from app.core.config import settings
from app.routers.accounts import router as accounts_router
from app.routers.ai_audit import router as ai_audit_router
from app.schemas.response import error_response


def create_application() -> FastAPI:
    """创建 FastAPI 应用实例"""
    
    application = FastAPI(
        title=settings.APP_NAME,
        description="""
## 🎯 像素视觉 Python FastApi 辅助服务端

PixVision 多平台账号检测 & AI 文案审核 API，采用 RESTful API 设计规范。

### ✨ 主要特性

- 🔍 **多平台支持**: 支持 B站、抖音、微博等多个平台
- 📊 **详细信息**: 获取用户完整信息
- 🤖 **AI 文案审核**: 智能内容审核，自动识别违规/中立/正常内容
- 🎨 **RESTful 设计**: 遵循 REST API 最佳实践
- ⚡ **高性能**: 基于 FastAPI 和异步 HTTP 客户端
- 📚 **友好文档**: 自动生成的交互式 API 文档
- 🔧 **易于扩展**: 模块化设计，轻松添加新平台

### 📝 API 规范

所有接口返回统一的 JSON 格式：
```json
{
  "code": 0,
  "message": "success",
  "data": {},
  "timestamp": "2024-01-01T12:00:00"
}
```

### 🚀 快速开始

**账号检测相关**
1. 检测账号是否存在: `GET /api/v1/accounts/{platform}/{user_id}`
2. 获取账号详细信息: `GET /api/v1/accounts/{platform}/{user_id}/info`
3. 查看支持的平台: `GET /api/v1/accounts/platforms`

**AI 文案审核相关**
1. 审核文案内容: `POST /api/v1/content/audit`
2. 查看 AI 配置状态: `GET /api/v1/content/config`
        """,
        version=settings.APP_VERSION,
        docs_url=None,  # 使用自定义文档路由
        redoc_url=None,
        contact={
            "name": "API Support",
            "email": "support@example.com",
        },
        license_info={
            "name": "MIT",
        },
    )
    
    # 添加 CORS 中间件
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 注册路由
    application.include_router(accounts_router, prefix=settings.API_V1_PREFIX)
    application.include_router(ai_audit_router, prefix=settings.API_V1_PREFIX)
    
    return application


# 创建应用实例
app = create_application()


@app.get("/", tags=["首页"])
async def root():
    """API 首页"""
    return {
        "message": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
        "api_v1": settings.API_V1_PREFIX,
        "examples": [
            f"{settings.API_V1_PREFIX}/accounts/bilibili/520500365",
            f"{settings.API_V1_PREFIX}/accounts/bilibili/520500365/info",
            f"{settings.API_V1_PREFIX}/accounts/platforms",
            f"{settings.API_V1_PREFIX}/content/audit",
            f"{settings.API_V1_PREFIX}/content/config"
        ]
    }


@app.get("/health", tags=["健康检查"])
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """自定义 Swagger UI 文档"""
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - API 文档",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
    )


@app.get("/redoc", include_in_schema=False)
async def custom_redoc_html():
    """自定义 ReDoc 文档"""
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title + " - ReDoc",
        redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js",
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
