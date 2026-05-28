"""
dict.py — 字典体系模型

三个模型构成完整的标签管理系统：
- DictTypes：定义标签类别（品类、区域、就餐方式等），标记属于哪张业务表
- DictData：具体的标签值（火锅、华农西门、堂食等）
- DictRel：将标签值多态关联到任意实体

设计理念：一切可枚举的标签属性通过字典管理，不创建硬编码字段。
"""

from tortoise import fields
from .base import BaseModel
from constants import DICT_TARGET_TABLES


class DictTypes(BaseModel):
    """
    DictTypes 表 — 字典类型表

    定义"这是什么类型的标签"。name 作为业务唯一标识。
    target_table 标记该字典类型归于哪张业务表，供前端/开发者过滤。
    """
    id = fields.IntField(pk=True, description="唯一标识")
    name = fields.CharField(max_length=50, unique=True, null=False, description="类型名称，如'品类'、'区域'、'就餐方式'")
    target_table = fields.CharField(
        max_length=50, null=False,
        description=f"所属业务表名。合法值：{DICT_TARGET_TABLES}"
    )
    description = fields.CharField(max_length=255, null=True, description="类型描述")
    sort_order = fields.IntField(default=0, description="排序顺序（类型间排序）")

    @classmethod
    def validate_target_table(cls, value: str) -> bool:
        """校验 target_table 是否在允许列表中"""
        return value in DICT_TARGET_TABLES

    class Meta:
        table = "dict_types"

    def __str__(self):
        return self.name


class DictData(BaseModel):
    """
    DictData 表 — 字典数据表

    具体的标签值。name 在同一个 DictType 下唯一。
    """
    id = fields.IntField(pk=True, description="唯一标识")
    dict_type = fields.ForeignKeyField(
        "models.DictTypes", related_name="dict_data",
        on_delete=fields.CASCADE, description="所属字典类型"
    )
    name = fields.CharField(max_length=50, null=False, description="标签名称，如'火锅'、'华农西门'")
    sort_order = fields.IntField(default=0, description="排序顺序（同一类型内）")
    is_default = fields.BooleanField(default=False, description="是否为默认值")
    extra = fields.JSONField(null=True, description="扩展字段，如存储图标URL、颜色值等")

    class Meta:
        table = "dict_data"
        unique_together = [("dict_type_id", "name")]

    def __str__(self):
        return self.name


class DictRel(BaseModel):
    """
    DictRel 表 — 字典数据关联表（多态）

    将 DictData 中的标签关联到任意实体。
    替代原有的 ShopDictRel，每新增一种可标签实体无需新建关联表。

    与 Images、ContentLikes 保持统一的多态设计风格。
    """
    id = fields.IntField(pk=True, description="唯一标识")
    entity_type = fields.CharField(max_length=32, null=False, description="关联实体类型，如 shop / complaint / user 等")
    entity_id = fields.BigIntField(null=False, description="关联实体主键 ID")
    dict_data = fields.ForeignKeyField(
        "models.DictData", related_name="dict_rels",
        on_delete=fields.CASCADE, description="字典数据ID"
    )

    class Meta:
        table = "dict_rels"
        unique_together = [("entity_type", "entity_id", "dict_data_id")]

    def __str__(self):
        return f"DictRel {self.id}: {self.entity_type} {self.entity_id} -> {self.dict_data}"
