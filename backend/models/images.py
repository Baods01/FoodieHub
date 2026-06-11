from tortoise.models import Model
from tortoise import fields
from .base import BaseModel


class Images(BaseModel):
    """
    Images 表 - 图片表

    多态关联设计（entity_type + entity_id）：
    - entity_type = 'shop' / 'menu_item' / 'shop_comment' / 'comment_reply' 等
    - 无 FK 约束是主动选择，级联删除在 DAO 层统一处理
    """
    id = fields.BigIntField(pk=True, description="图片唯一标识")
    url = fields.CharField(max_length=255, null=False, description="图片访问路径（相对路径或 CDN 地址）")
    entity_type = fields.CharField(max_length=32, null=False, description='关联实体类型，如 shop、menu_item、shop_comment 等')
    entity_id = fields.BigIntField(null=False, description="对应实体的主键 ID（BigInt 兼容所有实体的主键类型）")
    file_size = fields.IntField(null=True, description="文件大小（字节）")
    width = fields.IntField(null=True, description="图片宽度（像素）")
    height = fields.IntField(null=True, description="图片高度（像素）")
    mime_type = fields.CharField(max_length=50, null=True, description="MIME 类型，如 image/jpeg")
    extra = fields.JSONField(null=True, description="扩展字段，存储 alt 文本等业务自定义信息")
    uploader_id = fields.IntField(null=True, description="上传者用户ID")

    class Meta:
        table = "images"
        indexes = [
            ("entity_type", "entity_id"),
        ]

    def __str__(self):
        return f"Image {self.id}: {self.url}"
