import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from datetime import datetime
from models.users import Users
from models.shops import Shops
from models.logs import UserBehaviorLogs
from main import app

# 创建测试客户端
client = TestClient(app)


@pytest.mark.asyncio
async def test_user_history_integration_with_existing_features():
    """测试浏览历史记录与现有功能的集成"""
    
    # 测试用户访问店铺时自动记录浏览历史
    with patch('dependencies.auth.get_current_user') as mock_auth:
        mock_user = Users(
            id=1,
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
            is_active=True
        )
        mock_auth.return_value = mock_user
        
        # 模拟店铺存在
        with patch('dao.shop_dao.ShopDAO.find_shop_by_id') as mock_find_shop:
            mock_shop = Shops(
                id=101,
                name="测试店铺",
                description="测试店铺描述",
                view_count=0,
                favorite_count=0,
                comment_count=0,
                average_rating=0.0,
                is_active=True
            )
            mock_find_shop.return_value = mock_shop
            
            # 模拟创建浏览记录
            with patch('dao.shop_dao.ShopDAO.create_view_log') as mock_create_log:
                mock_create_log.return_value = UserBehaviorLogs(
                    id=1,
                    user_id=1,
                    behavior_type="view_shop",
                    target_type="shop",
                    target_id=101,
                    is_active=True
                )
                
                # 模拟获取店铺详情（会触发浏览记录创建）
                response = client.get("/shops/101")
                assert response.status_code == 200
                
                # 验证浏览记录已创建
                mock_create_log.assert_called_once()


@pytest.mark.asyncio
async def test_browse_history_with_filtering():
    """测试浏览历史记录的筛选功能"""
    with patch('dependencies.auth.get_current_user') as mock_auth:
        mock_user = Users(
            id=1,
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
            is_active=True
        )
        mock_auth.return_value = mock_user
        
        # 测试时间范围筛选
        with patch('dao.shop_dao.ShopDAO.get_user_view_history_with_shop_info') as mock_get_history:
            with patch('dao.shop_dao.ShopDAO.count_user_view_history_with_filters') as mock_count:
                mock_get_history.return_value = []
                mock_count.return_value = 0
                
                # 发送带时间筛选参数的请求
                response = client.get("/user/history/?start_time=2023-01-01&end_time=2023-12-31")
                assert response.status_code == 200
                
                # 测试店铺ID筛选
                response = client.get("/user/history/?shop_id=101")
                assert response.status_code == 200


@pytest.mark.asyncio
async def test_user_history_pagination():
    """测试浏览历史记录的分页功能"""
    with patch('dependencies.auth.get_current_user') as mock_auth:
        mock_user = Users(
            id=1,
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
            is_active=True
        )
        mock_auth.return_value = mock_user
        
        with patch('dao.shop_dao.ShopDAO.get_user_view_history_with_shop_info') as mock_get_history:
            with patch('dao.shop_dao.ShopDAO.count_user_view_history_with_filters') as mock_count:
                # 模拟返回多条记录
                mock_get_history.return_value = [
                    {
                        "id": 1,
                        "shop": {
                            "id": 101,
                            "name": "测试店铺1",
                            "view_count": 10,
                            "favorite_count": 5,
                            "comment_count": 3,
                            "average_rating": 4.5,
                            "aliases": [],
                            "merged_into_id": None,
                            "price_range": "中档",
                            "business_hours": "10:00-22:00",
                            "dining_methods": ["堂食", "外卖"],
                            "address_detail": "测试地址1",
                            "tags": ["特色菜", "推荐"],
                            "created_at": datetime.now(),
                            "updated_at": datetime.now()
                        },
                        "viewed_at": datetime.now(),
                        "updated_at": datetime.now()
                    },
                    {
                        "id": 2,
                        "shop": {
                            "id": 102,
                            "name": "测试店铺2",
                            "view_count": 15,
                            "favorite_count": 8,
                            "comment_count": 5,
                            "average_rating": 4.2,
                            "aliases": [],
                            "merged_into_id": None,
                            "price_range": "高档",
                            "business_hours": "11:00-23:00",
                            "dining_methods": ["堂食"],
                            "address_detail": "测试地址2",
                            "tags": ["精品", "推荐"],
                            "created_at": datetime.now(),
                            "updated_at": datetime.now()
                        },
                        "viewed_at": datetime.now(),
                        "updated_at": datetime.now()
                    }
                ]
                mock_count.return_value = 2
                
                # 测试分页参数
                response = client.get("/user/history/?page=1&page_size=1")
                assert response.status_code == 200
                data = response.json()
                assert data["items"] == []
                assert data["total"] == 2
                assert data["page"] == 1
                assert data["page_size"] == 1
                assert data["total_pages"] == 2