import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from datetime import datetime
from models.users import Users
from models.shops import Shops
from models.logs import UserBehaviorLogs
from main import app
from schemas.users import UserResponse

# 创建测试客户端
client = TestClient(app)


def test_get_user_history_unauthorized():
    """测试未授权访问浏览历史接口"""
    response = client.get("/user/history/")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_user_history_authorized():
    """测试已授权用户获取浏览历史"""
    # 模拟用户登录
    with patch('dependencies.auth.get_current_user') as mock_auth:
        mock_user = Users(
            id=1,
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
            is_active=True
        )
        mock_auth.return_value = mock_user
        
        # 模拟DAO方法返回
        with patch('dao.shop_dao.ShopDAO.get_user_view_history_with_shop_info') as mock_get_history:
            with patch('dao.shop_dao.ShopDAO.count_user_view_history_with_filters') as mock_count:
                mock_get_history.return_value = [
                    {
                        "id": 1,
                        "shop": {
                            "id": 101,
                            "name": "测试店铺",
                            "view_count": 10,
                            "favorite_count": 5,
                            "comment_count": 3,
                            "average_rating": 4.5,
                            "aliases": [],
                            "merged_into_id": None,
                            "price_range": "中档",
                            "business_hours": "10:00-22:00",
                            "dining_methods": ["堂食", "外卖"],
                            "address_detail": "测试地址",
                            "tags": ["特色菜", "推荐"],
                            "created_at": datetime.now(),
                            "updated_at": datetime.now()
                        },
                        "viewed_at": datetime.now(),
                        "updated_at": datetime.now()
                    }
                ]
                mock_count.return_value = 1
                
                # 发送请求
                response = client.get("/user/history/")
                assert response.status_code == 200
                data = response.json()
                assert "items" in data
                assert "total" in data
                assert data["total"] == 1


@pytest.mark.asyncio
async def test_delete_history_item_unauthorized():
    """测试未授权删除浏览历史"""
    response = client.delete("/user/history/1")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_history_item_authorized_success():
    """测试已授权用户成功删除浏览历史"""
    with patch('dependencies.auth.get_current_user') as mock_auth:
        mock_user = Users(
            id=1,
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
            is_active=True
        )
        mock_auth.return_value = mock_user
        
        # 模拟DAO方法返回成功
        with patch('dao.shop_dao.ShopDAO.delete_view_history_item') as mock_delete:
            mock_delete.return_value = True
            
            response = client.delete("/user/history/1")
            assert response.status_code == 200
            assert response.json() == {"message": "删除成功"}


@pytest.mark.asyncio
async def test_delete_history_item_not_found():
    """测试删除不存在的浏览历史记录"""
    with patch('dependencies.auth.get_current_user') as mock_auth:
        mock_user = Users(
            id=1,
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
            is_active=True
        )
        mock_auth.return_value = mock_user
        
        # 模拟DAO方法返回失败
        with patch('dao.shop_dao.ShopDAO.delete_view_history_item') as mock_delete:
            mock_delete.return_value = False
            
            response = client.delete("/user/history/999")
            assert response.status_code == 404
            assert "浏览历史记录不存在或不属于当前用户" in response.json()["detail"]


@pytest.mark.asyncio
async def test_clear_all_history_unauthorized():
    """测试未授权清空浏览历史"""
    response = client.delete("/user/history/")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_clear_all_history_authorized():
    """测试已授权用户清空浏览历史"""
    with patch('dependencies.auth.get_current_user') as mock_auth:
        mock_user = Users(
            id=1,
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
            is_active=True
        )
        mock_auth.return_value = mock_user
        
        # 模拟DAO方法返回
        with patch('dao.shop_dao.ShopDAO.clear_user_view_history') as mock_clear:
            mock_clear.return_value = 5
            
            response = client.delete("/user/history/")
            assert response.status_code == 200
            data = response.json()
            assert data["deleted_count"] == 5