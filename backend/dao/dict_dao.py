"""
dict_dao.py — 字典体系数据访问层

对应 models/dict.py：DictTypes / DictData / DictRel
"""

from typing import Optional, List
from models.dict import DictTypes, DictData, DictRel


class DictTypeDAO:
    """字典类型表 — DictTypes"""

    @staticmethod
    async def get_by_id(id: int) -> Optional[DictTypes]:
        return await DictTypes.get_or_none(id=id, is_active=True)

    @staticmethod
    async def get_by_name(name: str) -> Optional[DictTypes]:
        return await DictTypes.get_or_none(name=name, is_active=True)

    @staticmethod
    async def get_all() -> List[DictTypes]:
        return await DictTypes.filter(is_active=True).order_by("sort_order", "id").all()

    @staticmethod
    async def create(name: str, target_table: str,
                     description: Optional[str] = None,
                     sort_order: int = 0) -> DictTypes:
        return await DictTypes.create(
            name=name,
            target_table=target_table,
            description=description,
            sort_order=sort_order,
        )

    @staticmethod
    async def update(id: int, **kwargs) -> Optional[DictTypes]:
        obj = await DictTypes.get_or_none(id=id, is_active=True)
        if not obj:
            return None
        for k, v in kwargs.items():
            setattr(obj, k, v)
        await obj.save()
        return obj

    @staticmethod
    async def delete(id: int) -> bool:
        obj = await DictTypes.get_or_none(id=id, is_active=True)
        if not obj:
            return False
        obj.is_active = False
        await obj.save()
        return True


class DictDataDAO:
    """字典数据表 — DictData"""

    @staticmethod
    async def get_by_id(id: int) -> Optional[DictData]:
        return await DictData.get_or_none(id=id, is_active=True)

    @staticmethod
    async def get_by_dict_type(dict_type_id: int) -> List[DictData]:
        return await DictData.filter(
            dict_type_id=dict_type_id, is_active=True
        ).order_by("sort_order", "id").all()

    @staticmethod
    async def get_by_type_name(type_name: str) -> List[DictData]:
        """
        按字典类型名称查询所有数据项。
        例如 get_by_type_name('品类') → [{"id":1, "name":"火锅"}, ...]
        """
        return await DictData.filter(
            dict_type__name=type_name, is_active=True
        ).order_by("sort_order", "id").all()

    @staticmethod
    async def get_by_name(type_name: str, data_name: str) -> Optional[DictData]:
        """
        精确定位：某类型下某名称的数据项。
        例如 get_by_name('品类', '火锅')
        """
        return await DictData.get_or_none(
            dict_type__name=type_name, name=data_name, is_active=True
        )

    @staticmethod
    async def create(dict_type_id: int, name: str,
                     sort_order: int = 0, is_default: bool = False,
                     extra: Optional[dict] = None) -> DictData:
        return await DictData.create(
            dict_type_id=dict_type_id,
            name=name,
            sort_order=sort_order,
            is_default=is_default,
            extra=extra,
        )

    @staticmethod
    async def update(id: int, **kwargs) -> Optional[DictData]:
        obj = await DictData.get_or_none(id=id, is_active=True)
        if not obj:
            return None
        for k, v in kwargs.items():
            setattr(obj, k, v)
        await obj.save()
        return obj

    @staticmethod
    async def delete(id: int) -> bool:
        obj = await DictData.get_or_none(id=id, is_active=True)
        if not obj:
            return False
        obj.is_active = False
        await obj.save()
        return True


class DictRelDAO:
    """字典关联表 — DictRel（多态）"""

    @staticmethod
    async def get_entity_dicts(entity_type: str, entity_id: int) -> list:
        """
        查某实体的全部标签，返回带类型信息的结构化数据。
        返回格式：
        [
            {"dict_type_name": "品类", "dict_data_id": 5, "dict_data_name": "火锅"},
            {"dict_type_name": "区域", "dict_data_id": 9, "dict_data_name": "华农西门"},
        ]
        """
        rels = await DictRel.filter(
            entity_type=entity_type, entity_id=entity_id, is_active=True
        ).select_related("dict_data", "dict_data__dict_type").all()

        result = []
        for rel in rels:
            dd = rel.dict_data
            if not dd or not dd.is_active:
                continue
            dt = dd.dict_type
            result.append({
                "dict_type_name": dt.name if dt and dt.is_active else None,
                "dict_data_id": dd.id,
                "dict_data_name": dd.name,
            })
        return result

    @staticmethod
    async def add_dict_to_entity(entity_type: str, entity_id: int,
                                 dict_data_id: int) -> DictRel:
        """为实体打标签。若已存在关联（含软删除）则恢复 is_active。"""
        existing = await DictRel.get_or_none(
            entity_type=entity_type, entity_id=entity_id,
            dict_data_id=dict_data_id,
        )
        if existing:
            if not existing.is_active:
                existing.is_active = True
                await existing.save()
            return existing
        return await DictRel.create(
            entity_type=entity_type, entity_id=entity_id,
            dict_data_id=dict_data_id,
        )

    @staticmethod
    async def remove_dict_from_entity(entity_type: str, entity_id: int,
                                      dict_data_id: int) -> bool:
        """移除实体的某个标签（软删除）。"""
        rel = await DictRel.get_or_none(
            entity_type=entity_type, entity_id=entity_id,
            dict_data_id=dict_data_id, is_active=True,
        )
        if not rel:
            return False
        rel.is_active = False
        await rel.save()
        return True

    @staticmethod
    async def clear_entity_dicts(entity_type: str, entity_id: int) -> int:
        """清除某实体的全部标签（实体被删除时调用）。返回影响的记录数。"""
        count = await DictRel.filter(
            entity_type=entity_type, entity_id=entity_id, is_active=True
        ).update(is_active=False)
        return count

    @staticmethod
    async def get_entities_by_dict(dict_data_id: int) -> List[int]:
        """反向查询：某个标签下的所有 entity_id。"""
        rels = await DictRel.filter(
            dict_data_id=dict_data_id, is_active=True
        ).all()
        return [r.entity_id for r in rels]
