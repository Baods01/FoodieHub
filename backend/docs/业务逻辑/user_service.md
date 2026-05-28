# user_service.py — 用户业务逻辑

> 面向：Router 层开发人员
> 文件位置：`services/user_service.py`

---

## 概述

UserService 提供用户注册、登录、认证、信息更新、账号删除等核心功能。

---

## 方法列表

| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `register(data)` | `UserCreate` | `UserResponse` | ⭐ 注册（含查重、密码哈希） |
| `login(login_type, account, password)` | 类型 + 账号 + 密码 | `LoginResponse` | ⭐ 登录，按类型（username/phone/email）精确匹配 |
| `authenticate(account, password)` | 同上 | `Optional[UserResponse]` | OAuth2 表单专用认证 |
| `get_by_id(user_id)` | int | `Optional[UserResponse]` | |
| `update_profile(user_id, data)` | `UserUpdate` | `Optional[UserResponse]` | 更新头像/简介/性别 |
| `ban_user(user_id)` | int | `bool` | 封禁用户 |
| `unban_user(user_id)` | int | `bool` | 解封用户 |
| `delete_account(user_id)` | int | `bool` | 软删除 |
| `list(is_active, is_banned, keyword, page, page_size)` | 筛选可选 | `dict` | 管理员用户列表 |

---

## 典型用法

```python
# 注册
try:
    user = await UserService.register(UserCreate(
        username="张三", password="pass123",
        phone="13800138000", email="zhangsan@example.com",
    ))
except ValueError as e:
    return {"error": str(e)}

# 登录
try:
    resp = await UserService.login("username", "张三", "pass123")
    token = resp.access_token
except ValueError as e:
    return {"error": str(e)}

# OAuth2 表单登录
user = await UserService.authenticate(form_data.username, form_data.password)
```

---

## 注意事项

1. **`login` 与 `authenticate` 的区别**：`login` 返回完整 `LoginResponse`（含 token），给自定义登录接口用；`authenticate` 只返回 `UserResponse`，给 OAuth2 `OAuth2PasswordRequestForm` 用。
2. **封禁用户**：`login` 对封禁用户拒绝登录并提示"账户已被封禁"；`authenticate` 返回 `None`（OAuth2 标准：不暴露封禁状态给未登录者）。
