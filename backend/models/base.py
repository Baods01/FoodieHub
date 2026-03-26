from tortoise.models import Model
from tortoise import fields


class TimestampMixin:
    """
    Mixin to add created_at and updated_at timestamps to models
    """
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="最后更新时间")


class SoftDeleteMixin:
    """
    Mixin to add soft delete functionality
    """
    is_active = fields.BooleanField(default=True, description="是否启用（软删除）")


class BaseModel(TimestampMixin, SoftDeleteMixin, Model):
    """
    Base model with common fields
    """
    class Meta:
        abstract = True