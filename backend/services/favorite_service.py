from dao.favorite_dao import FavoriteDAO
from schemas.favorites import FavoriteResponse


class FavoriteService:
    """收藏业务逻辑"""

    @staticmethod
    async def toggle(user_id: int, shop_id: int) -> dict:
        is_fav = await FavoriteDAO.is_favorited(user_id, shop_id)
        if is_fav:
            await FavoriteDAO.remove(user_id, shop_id)
        else:
            await FavoriteDAO.create(user_id, shop_id)
        count = await FavoriteDAO.count_by_shop(shop_id)
        return {"is_favorited": not is_fav, "favorite_count": count}

    @staticmethod
    async def list(user_id: int, page: int = 1, page_size: int = 20) -> dict:
        result = await FavoriteDAO.list_by_user(user_id, page=page, page_size=page_size)
        items = []
        for fav in result["items"]:
            # 手动提取 shop 关联字段（model_validate 无法自动从外键提取 shop_name）
            shop = getattr(fav, "shop", None)
            items.append({
                "id": fav.id,
                "user_id": fav.user_id,
                "shop_id": fav.shop_id,
                "shop_name": shop.name if shop else None,
                "shop_cover": shop.cover_image if shop else None,
                "created_at": fav.created_at.isoformat(),
            })
        return {
            "items": items,
            "total": result["total"],
            "page": result["page"],
            "page_size": result["page_size"],
        }

    @staticmethod
    async def list_shop_ids(user_id: int):
        return await FavoriteDAO.get_shop_ids_by_user(user_id)
