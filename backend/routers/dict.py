from fastapi import APIRouter, HTTPException, status, Query
from typing import Optional

from schemas.common import ResponseModel
from services import DictService

router = APIRouter(prefix="/dict", tags=["字典模块"])


@router.get("/types", response_model=ResponseModel, summary="所有字典类型")
async def list_dict_types():
    """返回全部字典类型列表（品类、区域、就餐方式等）。"""
    data = await DictService.list_types()
    return ResponseModel.success(data=data)


@router.get("/types/{type_id}", response_model=ResponseModel, summary="字典类型详情（含数据项）")
async def get_dict_type(type_id: int):
    """返回某字典类型及其下的所有字典数据项。"""
    tree = await DictService.list_types_with_children()
    for t in tree:
        if t.id == type_id:
            return ResponseModel.success(data=t)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="字典类型不存在")


@router.get("/data", response_model=ResponseModel, summary="按类型名称查字典数据")
async def get_dict_data(type_name: str = Query(..., description="字典类型名称，如'品类'、'区域'")):
    """返回某字典类型下的所有数据项。"""
    data = await DictService.list_data_by_type_name(type_name)
    return ResponseModel.success(data=data)
