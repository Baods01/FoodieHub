"""
images.py — 图片上传与查询路由
"""

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status, Query
from typing import Optional
from pathlib import Path
import uuid
import os

from schemas.common import ResponseModel
from schemas.users import UserResponse
from dao.image_dao import ImageDAO
from utils.auth import require_login

router = APIRouter(prefix="/images", tags=["图片模块"])

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "static" / "images"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


@router.post("/upload", response_model=ResponseModel, summary="上传图片")
async def upload_image(
    file: UploadFile = File(...),
    entity_type: str = Form(...),
    entity_id: int = Form(...),
    current_user: UserResponse = Depends(require_login),
):
    # 校验文件类型
    ext = Path(file.filename).suffix.lower() if file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件格式: {ext}，支持 {ALLOWED_EXTENSIONS}",
        )

    # 校验文件大小
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"文件过大（{len(contents)}），最大 {MAX_FILE_SIZE} bytes",
        )

    # 保存文件
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = UPLOAD_DIR / filename
    with open(filepath, "wb") as f:
        f.write(contents)

    # 写入数据库
    url = f"/static/images/{filename}"
    img = await ImageDAO.create(
        url=url,
        entity_type=entity_type,
        entity_id=entity_id,
        file_size=len(contents),
        mime_type=file.content_type,
    )

    return ResponseModel.success(data={"id": img.id, "url": url}, message="上传成功")


@router.get("", response_model=ResponseModel, summary="按实体类型获取图片列表")
async def list_images_by_entity(
    entity_type: str = Query(..., description="实体类型，如 'shop'"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(50, ge=1, le=200, description="每页数量"),
    order: str = Query("random", pattern="^(random|newest)$", description="排序方式：random=随机，newest=最新"),
):
    """
    按实体类型获取图片列表
    
    查询参数:
    - entity_type (string, 必填): 实体类型，如 'shop'
    - page (int, 可选): 页码，默认 1
    - page_size (int, 可选): 每页数量，默认 50，最大 200
    - order (string, 可选): 排序方式，random=随机，newest=最新，默认 random
    
    响应:
    - 成功返回图片列表
    - 失败返回错误信息
    """
    data = await ImageDAO.list_by_entity_type(
        entity_type=entity_type,
        page=page,
        page_size=page_size,
        order=order,
    )
    return ResponseModel.success(data=data, message="获取成功")
