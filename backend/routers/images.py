"""
images.py — 图片上传与查询路由
"""

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
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
    """
    上传图片接口
    
    表单参数:
    - file (file, 必填): 要上传的文件
    - entity_type (string, 必填): 关联实体类型
    - entity_id (integer, 必填): 关联实体ID
    
    响应:
    - 成功返回图片信息
    - 失败返回错误信息
    """
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
