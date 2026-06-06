"""
应用配置 — 通过 .env 文件注入敏感值，不硬编码密码/密钥。

开发者流程：
  1. cp .env.example .env
  2. 编辑 .env 填入自己的数据库密码和 JWT 密钥
  3. 不要将 .env 提交到 Git

使用方式：
  from config import settings
  settings.DATABASE_URL  → 读取 .env 中的值或默认值
"""

import os
from pydantic_settings import BaseSettings
from typing import Dict, Any, List


class Settings(BaseSettings):
    """应用配置，优先从 .env 文件读取"""

    # ——— 应用元信息 ———
    APP_NAME: str = "FoodieHub"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # ——— 数据库 ———
    DATABASE_URL: str = "mysql://root:@localhost:3306/foodiehub"

    # ——— JWT ———
    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440         # 24 小时
    REMEMBER_ME_EXPIRE_DAYS: int = 30

    # ——— CORS ———
    CORS_ORIGINS: List[str] = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]

    # ——— Aerich / Tortoise ORM 配置（动态构建，避免连接串写两遍） ———
    @property
    def TORTOISE_ORM(self) -> Dict[str, Any]:
        return {
            "connections": {"default": self.DATABASE_URL},
            "apps": {
                "models": {
                    "models": ["models", "aerich.models"],
                    "default_connection": "default",
                },
            },
        }

    class Config:
        env_file = os.path.join(os.path.dirname(__file__), ".env")
        env_file_encoding = "utf-8"


settings = Settings()
