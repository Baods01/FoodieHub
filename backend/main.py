from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.staticfiles import StaticFiles
from tortoise.contrib.fastapi import register_tortoise

from config import settings
from routers.users import router as users_router
from routers.shops import router as shops_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    print(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} 启动中...")
    yield
    # 关闭时执行
    print(f"👋 {settings.APP_NAME} 正在关闭...")


# 创建 FastAPI 应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="美食点评平台 API",
    lifespan=lifespan,
    docs_url=None,  # 自定义 docs 路由
    swagger_ui_init_oauth={
        "clientId": "swagger-ui",
        "clientSecret": "",
        "realm": "foodiehub",
        "appName": "FoodieHub",
        "scopeSeparator": " ",
        "scopes": "openid profile email",
        "usePkceWithAuthorizationCodeGrant": True,
    },
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# 注册 Tortoise ORM
register_tortoise(
    app,
    config={
        "connections": {"default": settings.DATABASE_URL},
        "apps": {
            "models": {
                "models": ["models", "aerich.models"],
                "default_connection": "default",
            },
        },
    },
    generate_schemas=False,  # 使用 aerich 管理迁移
    add_exception_handlers=True,
)

# 注册路由
app.include_router(users_router, tags=["用户模块"])
app.include_router(shops_router, tags=["店铺模块"])

# 配置静态文件服务（图片）
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# 自定义 Swagger UI 路由（支持 OAuth2）
@app.get("/docs", include_in_schema=False)
async def get_swagger_ui():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="FoodieHub API",
        oauth2_redirect_url="/docs/oauth2-redirect",
        swagger_ui_parameters={
            "oauth2RedirectUrl": "/docs/oauth2-redirect",
        },
    )

@app.get("/docs/oauth2-redirect", include_in_schema=False)
async def oauth2_redirect():
    return get_swagger_ui_oauth2_redirect_html()


# 健康检查
@app.get("/health", tags=["系统"])
async def health_check():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=settings.DEBUG,
    )