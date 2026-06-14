"""
dict_service.py — 字典业务逻辑

"字典"是什么？
  字典体系是 FoodieHub 的"标签系统"。它由三层组成：
  1. DictType（字典类型）：如"品类"、"区域"、"就餐方式"
  2. DictData（字典数据）：如品类下的"中餐"、"西餐"；区域下的"华山区"、"泰山区"
  3. DictRel（字典关联）：记录"某个店铺被标记为哪些标签"，多对多关系

  用字典体系管理标签的好处：
  - 新增标签不需要改数据库表结构（不需要新增字段或新建表）
  - 标签有类型归类，管理后台可以统一维护
  - 支持多标签筛选（如搜索：品类=中餐 AND 区域=华山区）

调用链路示例（创建店铺时打标签）：
  ShopService.create()
    → DictRelDAO.add_dict_to_entity("shop", shop_id, dict_data_id)
      → DictRel.create(entity_type="shop", entity_id=shop_id, dict_data_id=dict_data_id)

本 Service 的方法都是简单的"透传"：
  调用 DictTypeDAO / DictDataDAO / DictRelDAO 的对应方法，然后用 Pydantic schema 序列化。
"""

from typing import Optional, List
from dao.dict_dao import DictTypeDAO, DictDataDAO, DictRelDAO
from schemas.dict import DictTypeResponse, DictDataResponse, DictTypeWithChildrenResponse


class DictService:
    """字典业务逻辑"""

    # ==================== DictType（字典类型） ====================

    @staticmethod
    async def get_type_by_id(id: int) -> Optional[DictTypeResponse]:
        """
        按 ID 获取单个字典类型。

        调用链路：DictTypeDAO.get_by_id(id)
          → DictType.get_or_none(id=id, is_active=True)
        返回 Pydantic schema 实例（用于 FastAPI 自动序列化）。
        """
        obj = await DictTypeDAO.get_by_id(id)
        return DictTypeResponse.model_validate(obj) if obj else None

    @staticmethod
    async def get_type_by_name(name: str) -> Optional[DictTypeResponse]:
        """按名称获取字典类型（如 get_type_by_name("品类")）。"""
        obj = await DictTypeDAO.get_by_name(name)
        return DictTypeResponse.model_validate(obj) if obj else None

    @staticmethod
    async def list_types() -> list[DictTypeResponse]:
        """
        获取所有字典类型列表。

        调用链路：DictTypeDAO.get_all()
          → DictType.filter(is_active=True).order_by("sort_order").all()
        """
        objs = await DictTypeDAO.get_all()
        return [DictTypeResponse.model_validate(o) for o in objs]

    @staticmethod
    async def list_types_with_children() -> list[DictTypeWithChildrenResponse]:
        """
        获取所有字典类型及其下属的字典数据（树形结构）。

        ★ 这是常见的"父子结构"查询模式：
          1. 先查所有父节点（DictType）
          2. 对每个父节点，查其子节点（DictData）
          3. 组装成嵌套结构

        [教师可能问：为什么不在 SQL 中用 JOIN 一次性查出？]
          答：因为 DictType 和 DictData 是两张独立的表，不存在 FK 关联的外键约束，
          DictData 的 dict_type_id 只是一个普通字段。在 Tortoise-ORM 中可以用 prefetch_related
          预加载，但当前方法在处理小数据量（字典类型通常不超过 20 个）时，
          简单的循环查询已经足够，且逻辑更直观。

        潜在风险：
          - 如果字典类型和数据量很大（如 100+ 类型，每种 1000+ 数据），
            这里的循环查询会产生 1（查类型）+ N（查数据）次查询。
            改进方案：先查所有 DictData，再在 Python 中按 dict_type_id 分组（group by）。
        """
        types = await DictTypeDAO.get_all()
        result = []
        for t in types:
            # ★ 对每个类型查一次 DictData，N+1 风险由此产生
            children = await DictDataDAO.get_by_dict_type(t.id)
            result.append(DictTypeWithChildrenResponse(
                # ★ ** 语法：将 DictTypeResponse 的字段展开后合并 children
                **DictTypeResponse.model_validate(t).model_dump(),
                children=[DictDataResponse.model_validate(c) for c in children],
            ))
        return result

    @staticmethod
    async def create_type(name: str, target_table: str,
                          description: Optional[str] = None,
                          sort_order: int = 0) -> DictTypeResponse:
        """创建新的字典类型。"""
        obj = await DictTypeDAO.create(
            name=name, target_table=target_table,
            description=description, sort_order=sort_order,
        )
        return DictTypeResponse.model_validate(obj)

    @staticmethod
    async def update_type(id: int, **kwargs) -> Optional[DictTypeResponse]:
        """更新字典类型。"""
        obj = await DictTypeDAO.update(id, **kwargs)
        return DictTypeResponse.model_validate(obj) if obj else None

    @staticmethod
    async def delete_type(id: int) -> bool:
        """软删除字典类型。"""
        return await DictTypeDAO.delete(id)

    # ==================== DictData（字典数据项） ====================

    @staticmethod
    async def get_data_by_id(id: int) -> Optional[DictDataResponse]:
        """按 ID 获取单个字典数据项。"""
        obj = await DictDataDAO.get_by_id(id)
        return DictDataResponse.model_validate(obj) if obj else None

    @staticmethod
    async def list_data_by_type(dict_type_id: int) -> list[DictDataResponse]:
        """按字典类型 ID 获取其下所有数据项。"""
        objs = await DictDataDAO.get_by_dict_type(dict_type_id)
        return [DictDataResponse.model_validate(o) for o in objs]

    @staticmethod
    async def list_data_by_type_name(type_name: str) -> list[DictDataResponse]:
        """
        按字典类型名称获取其下所有数据项。

        ★ 调用链路：
          DictDataDAO.get_by_type_name(type_name)
            → 内部通过 type name 查到 DictType，再 filter DictData
            实际 SQL：SELECT * FROM dict_data WHERE dict_type_id IN (SELECT id FROM dict_types WHERE name=?)
        """
        objs = await DictDataDAO.get_by_type_name(type_name)
        return [DictDataResponse.model_validate(o) for o in objs]

    @staticmethod
    async def create_data(dict_type_id: int, name: str, **kwargs) -> DictDataResponse:
        """在指定类型下创建新的数据项。"""
        obj = await DictDataDAO.create(dict_type_id=dict_type_id, name=name, **kwargs)
        return DictDataResponse.model_validate(obj)

    @staticmethod
    async def update_data(id: int, **kwargs) -> Optional[DictDataResponse]:
        """更新字典数据项。"""
        obj = await DictDataDAO.update(id, **kwargs)
        return DictDataResponse.model_validate(obj) if obj else None

    @staticmethod
    async def delete_data(id: int) -> bool:
        """软删除字典数据项。"""
        return await DictDataDAO.delete(id)

    # ==================== DictRel（实体-字典关联） ====================
    #
    # 这部分方法被 ShopService 大量使用：
    #   - 创建店铺时：DictRelDAO.add_dict_to_entity("shop", shop_id, dict_data_id)
    #   - 更新标签时：DictRelDAO.clear_entity_dicts() + 循环 add
    #   - 搜索店铺时：DictRelDAO.get_entity_dicts() 获取标签详情
    #
    # DictRel 表是多表关联的"中间表"：
    #   entity_type = "shop"  表示这是店铺的标签
    #   entity_id   = shop_id 表示关联的店铺 ID
    #   dict_data_id         表示关联的标签 ID
    #   如果将来需要给"用户"打标签（如用户偏好），只需 entity_type="user"，
    #   不需要新建关联表。这就是多态关联的扩展性优势。
    # =============================================================================

    @staticmethod
    async def get_entity_dicts(entity_type: str, entity_id: int) -> list:
        """获取某实体的所有标签（用于详情展示）。"""
        return await DictRelDAO.get_entity_dicts(entity_type, entity_id)

    @staticmethod
    async def add_dict_to_entity(entity_type: str, entity_id: int, dict_data_id: int):
        """给某实体添加一个标签。"""
        await DictRelDAO.add_dict_to_entity(entity_type, entity_id, dict_data_id)

    @staticmethod
    async def remove_dict_from_entity(entity_type: str, entity_id: int, dict_data_id: int) -> bool:
        """移除某实体的一个标签（软删除）。"""
        return await DictRelDAO.remove_dict_from_entity(entity_type, entity_id, dict_data_id)

    @staticmethod
    async def clear_entity_dicts(entity_type: str, entity_id: int) -> int:
        """
        清除某实体的所有标签（用于"替换标签"场景）。

        ★ 使用场景（见 ShopService.update）：
          当管理员修改店铺的标签时，流程是：
          1. clear_entity_dicts("shop", shop_id)  ← 清空旧标签
          2. 循环 add_dict_to_entity  ← 打上新标签

          这种"先删后增"的模式比"比较新旧差异后再增删"更简单，
          对于标签数量少（通常不超过 10 个）的场景，开销可以接受。
        """
        return await DictRelDAO.clear_entity_dicts(entity_type, entity_id)