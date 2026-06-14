"""
user_service.py — 用户业务逻辑

用户模块是项目的核心基础模块，负责注册、登录、认证、资料管理。
相比其他 Service，本模块的特点是：

1. 使用了 utils/password.py（密码哈希）和 utils/auth.py（JWT 生成）
2. 注册时自动查重（用户名/手机号/邮箱）
3. 登录支持三种方式（用户名/手机号/邮箱），且区分"账号不存在"和"账号被封禁"
4. 管理员封禁/解封操作通过透传调用 DAO

调用链路总览：
  Router（routers/auth.py）
    → UserService.register()
      → UserDAO.check_duplicate()    ← 查重
      → utils/password.hash_password()  ← 哈希
      → UserDAO.create()             ← 插入
    → UserService.login()
      → UserDAO.get_by_phone()/etc.  ← 查用户
      → utils/password.verify_password() ← 校验
      → utils/auth.create_access_token() ← 签发 JWT

[教师可能问：注册和登录的异常提示"账号或密码错误"和"XX已存在"是否泄露了用户信息？]
  答：这是一个安全与用户体验的权衡：
  - 注册时的"用户名已存在"提示会告诉攻击者"这个用户名被人注册了"，
    但因为我们允许使用手机号/邮箱登录，用户名本身不是敏感信息。
  - 登录时的"账号或密码错误"是统一提示，不暴露"到底是账号不存在还是密码错误"，
    这样可以防止攻击者通过枚举手段确认哪些账号已注册。
  - 被封禁的用户在登录时会收到"您的账户已被封禁"的明确提示，
    这需要用户先通过密码验证，不会泄露给未授权的人。
"""

from typing import Optional
from datetime import datetime, timedelta
from jose import jwt

from config import settings
from dao.user_dao import UserDAO
from utils.auth import create_access_token
from utils.password import hash_password, verify_password
from schemas.users import (
    UserCreate, UserResponse, LoginResponse, UserUpdate,
)


class UserService:
    """用户业务逻辑"""

    @staticmethod
    async def register(data: UserCreate) -> UserResponse:
        """
        用户注册。

        ★ 执行顺序：
          1. 查重：调用 UserDAO.check_duplicate() 检查用户名/手机号/邮箱是否已存在
             → 该方法在 DAO 层面做了三次独立的 SELECT EXISTS 查询
             → 返回第一个冲突的字段名（"username"/"phone"/"email"）
          2. 如果存在冲突，抛出 ValueError（由 Router 层捕获返回 400）
          3. 哈希密码：passlib 的 bcrypt 算法，输出格式 $2b$12$...
          4. 调用 UserDAO.create() 插入用户记录
          5. 返回 UserResponse（Pydantic schema 自动序列化）

        [教师可能问：check_duplicate 为什么是三次查询而不是一次 OR 组合？]
          答：因为我们需要告诉前端"到底是哪个字段重复了"。
          如果用 OR 组合查，只能知道"是否有重复"但不知道具体哪个字段。
          三次查询虽然多了两次数据库交互，但用户体验更好。
          如果性能成为瓶颈，可以用一条 SQL 加 CASE WHEN 实现：
            SELECT
              MAX(CASE WHEN username=? THEN 'username' END),
              MAX(CASE WHEN phone=? THEN 'phone' END),
              MAX(CASE WHEN email=? THEN 'email' END)
            FROM users WHERE is_active=1
        """
        dupe = await UserDAO.check_duplicate(data.username, data.phone, data.email)
        if dupe:
            labels = {"username": "用户名", "phone": "手机号", "email": "邮箱"}
            raise ValueError(f"{labels.get(dupe, dupe)}已存在")

        # ★ 关键：密码在存入数据库之前必须哈希，绝不能存明文
        # 哈希过程不可逆，即使用户数据库泄露，攻击者也无法直接拿到密码原文
        hashed = hash_password(data.password)
        user = await UserDAO.create(
            username=data.username, password=hashed,
            phone=data.phone, email=data.email,
        )
        return UserResponse.model_validate(user)

    @staticmethod
    async def login(login_type: str, account: str, password: str) -> LoginResponse:
        """
        用户登录（三种方式：username / phone / email）。

        ★ 执行顺序：
          1. 根据 login_type 调用不同的 DAO 方法查询用户
             - username → get_by_username(account)
             - phone    → get_by_phone(account)
             - email    → get_by_email(account)
             ★ 这些方法都加了 is_active=True 过滤，被封禁/注销的用户不会被查到
          2. 如果用户不存在，抛出 "账号或密码错误"（统一提示不暴露细节）
          3. 校验密码：verify_password() 底层调用 passlib 的 bcrypt.verify
             ★ bcrypt 会从哈希串中提取盐值，对密码原文加盐后再比较
          4. 检查用户状态：封禁或软删除的用户不能登录
          5. 签发 JWT Token（见 utils/auth.py 的 create_access_token）
             → token 的 payload 包含 exp（过期时间）和 sub（用户 ID）
          6. 返回 LoginResponse（含 token 和用户信息）

        [教师可能问：verify_password 是如何工作的？]
          答：bcrypt 的密码哈希结构是 $algorithm$cost$salt+hash。
          verify_password 从已存储的哈希串中提取出 salt，
          对用户输入的明文密码加盐后重新计算哈希，与存储的哈希比对。
          因为 salt 是随机的，即使两个用户密码相同，存储的哈希也不同。
          这避免了彩虹表攻击。
        """
        if login_type == "username":
            user = await UserDAO.get_by_username(account)
        elif login_type == "phone":
            user = await UserDAO.get_by_phone(account)
        elif login_type == "email":
            user = await UserDAO.get_by_email(account)
        else:
            raise ValueError("无效的登录方式")

        if not user:
            raise ValueError("账号或密码错误")

        # ★ 密码校验
        if not verify_password(password, user.password):
            raise ValueError("账号或密码错误")

        # ★ 状态检查（两个条件分别对应"软删除"和"封禁"）
        if not user.is_active:
            raise ValueError("您的账户已被封禁")
        if user.is_banned:
            raise ValueError("您的账户已被封禁")

        token = create_access_token(user.id)
        return LoginResponse(
            access_token=token,
            token_type="bearer",
            user=UserResponse.model_validate(user),
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    @staticmethod
    async def authenticate(account: str, password: str) -> Optional[UserResponse]:
        """
        OAuth2 表单登录专用（用于 Swagger UI 的 Authorize 功能）。

        与 login 的区别：
        - 不接受 login_type 参数，自动按"用户名/手机号/邮箱"匹配
        - 使用 get_by_account_include_banned 查询（包含被封禁用户）
        - 返回 None 而不是抛出异常（符合 OAuth2PasswordRequestForm 的使用习惯）
        - 不生成 token（由 Router 层调用 create_access_token 生成）

        [教师可能问：为什么需要两个登录方法？]
          答：login 是我们自定义的 JSON 登录接口（返回含用户信息的完整响应）；
          authenticate 是 FastAPI 标准 OAuth2 密码流的接口（只返回 token），
          用于 Swagger UI 的"Authorize"按钮。两者面向不同客户端。
        """
        user = await UserDAO.get_by_account_include_banned(account)
        if not user or not verify_password(password, user.password):
            return None
        if not user.is_active or user.is_banned:
            return None
        return UserResponse.model_validate(user)

    @staticmethod
    async def get_by_id(user_id: int) -> Optional[UserResponse]:
        """获取单个用户（用于个人中心页面）。"""
        user = await UserDAO.get_by_id(user_id)
        return UserResponse.model_validate(user) if user else None

    @staticmethod
    async def update_profile(user_id: int, data: UserUpdate) -> Optional[UserResponse]:
        """
        更新用户资料。

        参数 data 是 UserUpdate Pydantic schema，只包含允许修改的字段。
        ★ model_dump(exclude_unset=True) 的用法：
          只序列化用户显式传了值的字段，没传的字段使用数据库原值。
          Pydantic v2 推荐 model_dump 替代 v1 的 dict()。
        """
        update_dict = data.model_dump(exclude_unset=True)
        if not update_dict:
            # 如果没有任何字段被修改，直接返回当前用户信息
            return await UserService.get_by_id(user_id)
        user = await UserDAO.update(user_id, **update_dict)
        return UserResponse.model_validate(user) if user else None

    @staticmethod
    async def ban_user(user_id: int) -> bool:
        """封禁用户（透传调用 DAO）。"""
        user = await UserDAO.update(user_id, is_banned=True)
        return user is not None

    @staticmethod
    async def unban_user(user_id: int) -> bool:
        """解封用户（透传调用 DAO）。"""
        user = await UserDAO.update(user_id, is_banned=False)
        return user is not None

    @staticmethod
    async def delete_account(user_id: int) -> bool:
        """注销账号（软删除）。"""
        return await UserDAO.delete(user_id)

    @staticmethod
    async def list(
        is_active: Optional[bool] = None,
        is_banned: Optional[bool] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """
        管理员后台用户列表（分页 + 筛选 + 搜索）。

        ★ 这段代码与 DAO 的 list 方法配合：
          UserDAO.list() 返回的是 Users 模型实例的列表和 total 计数。
          Service 层在这里做了一次"格式转换"，将 ORM 模型实例转为纯 dict。
          重复了 UserResponse schema 的字段定义。

        [教师可能问：为什么这里手动序列化 dict，而不是用 UserResponse schema？]
          答：UserResponse 可能包含一些不需要在管理后台暴露的字段（如 password_hash？虽然她不存在），
          也缺少 is_active 等管理字段。手动序列化可以灵活控制返回哪些字段。
          更好的做法是定义一个 AdminUserResponse schema，包含管理后台需要的所有字段。
        """
        result = await UserDAO.list(
            is_active=is_active, is_banned=is_banned,
            keyword=keyword, page=page, page_size=page_size,
        )
        items = []
        for u in result["items"]:
            items.append({
                "id": u.id,
                "username": u.username,
                "phone": u.phone,
                "email": u.email,
                "avatar": u.avatar,
                "bio": u.bio,
                "role": u.role,
                "is_banned": u.is_banned,
                "is_active": u.is_active,
                "created_at": u.created_at.isoformat(),
            })
        return {"items": items, "total": result["total"], "page": result["page"], "page_size": result["page_size"]}