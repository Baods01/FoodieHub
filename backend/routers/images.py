"""
images.py — 图片上传、查询与删除路由
"""

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status, Path as PathParam
from typing import Optional
from pathlib import Path
import uuid
import os

from schemas.common import ResponseModel
from schemas.users import UserResponse
from schemas.images import ImageResponse
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
            detail="文件过大，最大支持 10MB",
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
        uploader_id=current_user.id,
    )

    return ResponseModel.success(data={"id": img.id, "url": url}, message="上传成功")


@router.delete("/{image_id}", response_model=ResponseModel, summary="删除图片")
async def delete_image(
    image_id: int = PathParam(..., description="图片ID"),
    current_user: UserResponse = Depends(require_login),
):
    """
    删除指定图片。

    权限校验：仅图片上传者或管理员可删除。
    删除时自动清理该图片的多态关联记录（DictRel）。
    """
    img = await ImageDAO.get_by_id(image_id)
    if not img:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="图片不存在或已被删除",
        )

    # 权限校验：上传者或管理员可删除
    if img.uploader_id != current_user.id and current_user.role != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除该图片",
        )

    # 级联删除（含 DictRel 清理）
    await ImageDAO.delete(image_id)

    # 删除本地文件
    if img.url and img.url.startswith("/static/images/"):
        file_path = BASE_DIR / img.url.lstrip("/")
        if file_path.exists():
            os.remove(file_path)

    return ResponseModel.success(message="删除成功")