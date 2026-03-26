from tortoise.models import Model
from tortoise import fields
from .base import BaseModel


class Images(BaseModel):
    """
    Images 表 - 图片表
    """
    id = fields.BigIntField(pk=True, description="图片唯一标识")
    url = fields.CharField(max_length=255, null=False, description="图片访问路径（建议存储相对路径或 CDN 地址）")
    entity_type = fields.CharField(max_length=32, null=False, description='关联实体类型，如 shop、menu_item、comment、question 等')
    entity_id = fields.IntField(null=False, description="对应实体的主键 ID")
    extra = fields.JSONField(null=True, description="扩展字段，存储图片宽高、文件大小、alt 文本等元数据")

    class Meta:
        table = "images"

    def __str__(self):
        return f"Image {self.id}: {self.url}"