"""
应用常量配置 — 与 .env / 密钥相关的配置放在 config.py，此处仅存放纯常量
"""

# ============ 图片上传限制 ============
ALLOWED_IMAGE_TYPES: list[str] = [
    "image/jpeg", "image/jpg", "image/png", "image/gif", "image/webp",
]
MAX_IMAGE_SIZE: int = 2 * 1024 * 1024  # 2MB

# ============ 分页 ============
PAGE_SIZE_DEFAULT: int = 20
PAGE_SIZE_MAX: int = 100

# ============ 用户角色 ============
ROLE_USER: int = 0
ROLE_ADMIN: int = 1

# ============ 字典表名枚举 ============
DICT_TARGET_TABLES: list[str] = [
    "shops",
    "complaints",
    "users",
    "menu_items",
]

# ============ 审核状态 ============
STATUS_PENDING: str = "pending"
STATUS_APPROVED: str = "approved"
STATUS_REJECTED: str = "rejected"
