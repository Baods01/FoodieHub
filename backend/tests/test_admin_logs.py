import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from datetime import datetime
from models.admin_logs import AdminOperationLog
from models.users import Users
from main import app
from utils.logger import log_database_error
from services.admin_log_service import AdminLogService

# 创建测试客户端
client = TestClient(app)


@pytest.mark.asyncio
async def test_create_admin_log():
    """测试创建管理员日志"""
    # 模拟管理员用户
    with patch('dependencies.auth.require_admin') as mock_auth:
        mock_user = Users(
            id=1,
            username="admin_test",
            email="admin@test.com",
            password_hash="hashed_password",
            is_active=True,
            role=1  # 管理员角色
        )
        mock_auth.return_value = mock_user
        
        # 测试创建日志
        response = client.post("/admin/logs/test", 
                             json={
                                 "operator_id": 1,
                                 "operator_account": "admin_test",
                                 "operation_type": "test_create",
                                 "operation_module": "test_module",
                                 "operation_ip": "127.0.0.1",
                                 "operation_description": "测试日志创建"
                             })
        
        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "日志创建成功"


@pytest.mark.asyncio
async def test_get_admin_logs():
    """测试查询管理员日志"""
    # 模拟管理员用户
    with patch('dependencies.auth.require_admin') as mock_auth:
        mock_user = Users(
            id=1,
            username="admin_test",
            email="admin@test.com",
            password_hash="hashed_password",
            is_active=True,
            role=1  # 管理员角色
        )
        mock_auth.return_value = mock_user
        
        # 测试查询日志
        response = client.get("/admin/logs?operator_id=1&page=1&page_size=10")
        
        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data


@pytest.mark.asyncio
async def test_export_admin_logs():
    """测试导出管理员日志"""
    # 模拟管理员用户
    with patch('dependencies.auth.require_admin') as mock_auth:
        mock_user = Users(
            id=1,
            username="admin_test",
            email="admin@test.com",
            password_hash="hashed_password",
            is_active=True,
            role=1  # 管理员角色
        )
        mock_auth.return_value = mock_user
        
        # 测试导出日志
        response = client.get("/admin/logs/export?operator_id=1")
        
        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


@pytest.mark.asyncio
async def test_delete_admin_log():
    """测试删除管理员日志"""
    # 模拟管理员用户
    with patch('dependencies.auth.get_current_admin_user') as mock_auth:
        mock_user = Users(
            id=1,
            username="admin_test",
            email="admin@test.com",
            password_hash="hashed_password",
            is_active=True,
            role=1  # 管理员角色
        )
        mock_auth.return_value = mock_user
        
        # 测试删除日志
        response = client.delete("/admin/logs/1")
        
        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "删除成功"