from typing import Optional, List
from dao.dict_dao import DictTypeDAO, DictDataDAO, DictRelDAO
from schemas.dict import DictTypeResponse, DictDataResponse, DictTypeWithChildrenResponse


class DictService:
    """字典业务逻辑"""

    # ==================== DictType ====================

    @staticmethod
    async def get_type_by_id(id: int) -> Optional[DictTypeResponse]:
        obj = await DictTypeDAO.get_by_id(id)
        return DictTypeResponse.model_validate(obj) if obj else None

    @staticmethod
    async def get_type_by_name(name: str) -> Optional[DictTypeResponse]:
        obj = await DictTypeDAO.get_by_name(name)
        return DictTypeResponse.model_validate(obj) if obj else None

    @staticmethod
    async def list_types() -> list[DictTypeResponse]:
        objs = await DictTypeDAO.get_all()
        return [DictTypeResponse.model_validate(o) for o in objs]

    @staticmethod
    async def list_types_with_children() -> list[DictTypeWithChildrenResponse]:
        types = await DictTypeDAO.get_all()
        result = []
        for t in types:
            children = await DictDataDAO.get_by_dict_type(t.id)
            result.append(DictTypeWithChildrenResponse(
                **DictTypeResponse.model_validate(t).model_dump(),
                children=[DictDataResponse.model_validate(c) for c in children],
            ))
        return result

    @staticmethod
    async def create_type(name: str, target_table: str,
                          description: Optional[str] = None,
                          sort_order: int = 0) -> DictTypeResponse:
        obj = await DictTypeDAO.create(
            name=name, target_table=target_table,
            description=description, sort_order=sort_order,
        )
        return DictTypeResponse.model_validate(obj)

    @staticmethod
    async def update_type(id: int, **kwargs) -> Optional[DictTypeResponse]:
        obj = await DictTypeDAO.update(id, **kwargs)
        return DictTypeResponse.model_validate(obj) if obj else None

    @staticmethod
    async def delete_type(id: int) -> bool:
        return await DictTypeDAO.delete(id)

    # ==================== DictData ====================

    @staticmethod
    async def get_data_by_id(id: int) -> Optional[DictDataResponse]:
        obj = await DictDataDAO.get_by_id(id)
        return DictDataResponse.model_validate(obj) if obj else None

    @staticmethod
    async def list_data_by_type(dict_type_id: int) -> list[DictDataResponse]:
        objs = await DictDataDAO.get_by_dict_type(dict_type_id)
        return [DictDataResponse.model_validate(o) for o in objs]

    @staticmethod
    async def list_data_by_type_name(type_name: str) -> list[DictDataResponse]:
        objs = await DictDataDAO.get_by_type_name(type_name)
        return [DictDataResponse.model_validate(o) for o in objs]

    @staticmethod
    async def create_data(dict_type_id: int, name: str, **kwargs) -> DictDataResponse:
        obj = await DictDataDAO.create(dict_type_id=dict_type_id, name=name, **kwargs)
        return DictDataResponse.model_validate(obj)

    @staticmethod
    async def update_data(id: int, **kwargs) -> Optional[DictDataResponse]:
        obj = await DictDataDAO.update(id, **kwargs)
        return DictDataResponse.model_validate(obj) if obj else None

    @staticmethod
    async def delete_data(id: int) -> bool:
        return await DictDataDAO.delete(id)

    # ==================== DictRel ====================

    @staticmethod
    async def get_entity_dicts(entity_type: str, entity_id: int) -> list:
        return await DictRelDAO.get_entity_dicts(entity_type, entity_id)

    @staticmethod
    async def add_dict_to_entity(entity_type: str, entity_id: int, dict_data_id: int):
        await DictRelDAO.add_dict_to_entity(entity_type, entity_id, dict_data_id)

    @staticmethod
    async def remove_dict_from_entity(entity_type: str, entity_id: int, dict_data_id: int) -> bool:
        return await DictRelDAO.remove_dict_from_entity(entity_type, entity_id, dict_data_id)

    @staticmethod
    async def clear_entity_dicts(entity_type: str, entity_id: int) -> int:
        return await DictRelDAO.clear_entity_dicts(entity_type, entity_id)
