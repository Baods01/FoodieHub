"""
image_dao.py — 图片数据访问层

对应 models/images.py：Images
多态关联（entity_type + entity_id），不跨表 JOIN。
"""

import random
from typing import Optional, List
from models.images import Images


class ImageDAO:
    """图片表 — Images"""

    # ==================== 基础 CRUD ====================

    @staticmethod
    async def get_by_id(id: int) -> Optional[Images]:
        return await Images.get_or_none(id=id, is_active=True)

    @staticmethod
    async def create(
        url: str,
        entity_type: str,
        entity_id: int,
        file_size: Optional[int] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        mime_type: Optional[str] = None,
        extra: Optional[dict] = None,
    ) -> Images:
        return await Images.create(
            url=url,
            entity_type=entity_type,
            entity_id=entity_id,
            file_size=file_size,
            width=width,
            height=height,
            mime_type=mime_type,
            extra=extra,
        )

    @staticmethod
    async def update(id: int, **kwargs) -> Optional[Images]:
        obj = await Images.get_or_none(id=id, is_active=True)
        if not obj:
            return None
        for k, v in kwargs.items():
            setattr(obj, k, v)
        await obj.save()
        return obj

    @staticmethod
    async def delete(id: int) -> bool:
        obj = await Images.get_or_none(id=id, is_active=True)
        if not obj:
            return False
        obj.is_active = False
        await obj.save()
        return True

    # ==================== 批量查询 ====================

    @staticmethod
    async def get_by_entity(entity_type: str, entity_id: int) -> List[Images]:
        """查某实体的全部图片，按 id 升序。"""
        return await Images.filter(
            entity_type=entity_type, entity_id=entity_id, is_active=True
        ).order_by("id").all()

    @staticmethod
    async def get_first_by_entity(entity_type: str, entity_id: int) -> Optional[Images]:
        """取某实体的第一张图片（封面图）。"""
        return await Images.filter(
            entity_type=entity_type, entity_id=entity_id, is_active=True
        ).order_by("id").first()

    # ==================== 级联清理 ====================

    @staticmethod
    async def clear_entity_images(entity_type: str, entity_id: int) -> int:
        """软删除某实体的全部图片。返回影响记录数。"""
        count = await Images.filter(
            entity_type=entity_type, entity_id=entity_id, is_active=True
        ).update(is_active=False)
        return count

    # ==================== 首页轮播图 ====================

    @staticmethod
    async def list_by_entity_type(
        entity_type: str,
        page: int = 1,
        page_size: int = 50,
        order: str = "random",
    ) -> dict:
        """
        按实体类型获取图片列表，支持随机排序。
        用于首页轮播图等聚合展示场景。
        """
        qs = Images.filter(entity_type=entity_type, is_active=True)

        total = await qs.count()

        # 全部查出并在 Python 层做排序/随机（数据量小，性能无影响）
        all_items = await qs.all()

        if order == "random":
            random.shuffle(all_items)
        else:
            all_items.sort(key=lambda i: i.created_at, reverse=True)

        offset = (page - 1) * page_size
        items = all_items[offset:offset + page_size]

        return {
            "items": [{"id": i.id, "url": i.url} for i in items],
            "total": total,
            "page": page,
            "page_size": page_size,
        }
