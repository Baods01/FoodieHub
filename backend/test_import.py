#!/usr/bin/env python
"""测试模块导入"""

try:
    from main import app
    print("✓ main.py 导入成功")
    
    from routers.comments_likes import router
    print("✓ routers/comments_likes.py 导入成功")
    
    from services.comments_likes_service import CommentsLikesService
    print("✓ services/comments_likes_service.py 导入成功")
    
    from dao.comments_likes_dao import CommentsLikesDAO
    print("✓ dao/comments_likes_dao.py 导入成功")
    
    from schemas.comments_likes import CommentLikeCreate, CommentLikeResponse
    print("✓ schemas/comments_likes.py 导入成功")
    
    # 新增动态模块测试
    from routers.user_activities import router as user_activities_router
    print("✓ routers/user_activities.py 导入成功")
    
    from services.user_activities_service import UserActivitiesService
    print("✓ services/user_activities_service.py 导入成功")
    
    from dao.user_activities_dao import UserActivitiesDAO
    print("✓ dao/user_activities_dao.py 导入成功")
    
    print("\n所有模块导入成功！")
    
except Exception as e:
    print(f"✗ 导入失败: {e}")
    import traceback
    traceback.print_exc()