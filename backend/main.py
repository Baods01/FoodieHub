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
from routers.auth import router as auth_router
from routers.shops import router as shops_router
from routers.interaction import router as interaction_router
from routers.messages import router as messages_router
from routers.admin import router as admin_router
from routers.dict import router as dict_router
from routers.activities import router as activities_router
from routers.history import router as history_router
from models import (
    Users, Activities, Favorites, Messages,
    Shops, Menu, Ratings,
    DictTypes, DictData, DictRel,
    Images,
    ShopComments, CommentReplies, ShopQuestions, QuestionAnswers, ContentLikes,
    Complaints, ShopEditRequests,
    OperationLog,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    from services import activity_signals  # noqa: F401
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="美食点评平台 API",
    lifespan=lifespan,
    docs_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

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
    generate_schemas=True,
    add_exception_handlers=True,
)

# 注册路由
app.include_router(auth_router)
app.include_router(shops_router)
app.include_router(interaction_router)
app.include_router(messages_router)
app.include_router(admin_router)
app.include_router(dict_router)
app.include_router(activities_router)
app.include_router(history_router)

# 配置静态文件服务
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


@app.get("/docs", include_in_schema=False)
async def get_swagger_ui():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="FoodieHub API",
        oauth2_redirect_url="/docs/oauth2-redirect",
    )


@app.get("/docs/oauth2-redirect", include_in_schema=False)
async def oauth2_redirect():
    return get_swagger_ui_oauth2_redirect_html()


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
