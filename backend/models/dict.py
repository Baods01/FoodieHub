from tortoise.models import Model
from tortoise import fields
from .base import BaseModel


class DictTypes(BaseModel):
    """
    DictTypes 表 - 字典类型表
    """
    id = fields.IntField(pk=True, description="唯一标识")
    code = fields.CharField(max_length=50, unique=True, null=False, description="类型编码，如 category、dining_method、location_type")
    name = fields.CharField(max_length=50, unique=True, null=False, description="类型名称，如店铺类别、点餐方式、位置类型")
    target_table = fields.CharField(max_length=50, null=False, description="目标表名，标识该字典类型属于哪个表，如 shops、users、menu_items")
    description = fields.CharField(max_length=255, null=True, description="类型描述")
    sort_order = fields.IntField(default=0, description="排序顺序（类型间排序）")

    class Meta:
        table = "dict_types"

    def __str__(self):
        return f"{self.name}({self.code})"


class DictData(BaseModel):
    """
    DictData 表 - 字典数据表
    """
    id = fields.IntField(pk=True, description="唯一标识")
    dict_type = fields.ForeignKeyField("models.DictTypes", related_name="dict_data", on_delete=fields.CASCADE, description="所属字典类型")
    code = fields.CharField(max_length=50, null=False, description="数据编码（同一类型内唯一），如 chinese_food")
    name = fields.CharField(max_length=50, null=False, description="显示名称，如中餐")
    value = fields.CharField(max_length=255, null=True, description="额外值（如保留原始值）")
    sort_order = fields.IntField(default=0, description="排序顺序（同一类型内）")
    is_default = fields.BooleanField(default=False, description="是否为默认值")
    extra = fields.JSONField(null=True, description="扩展字段（如存储图标、颜色等）")

    class Meta:
        table = "dict_data"
        # 唯一约束：防止同一类型下重复编码
        unique_together = [("dict_type_id", "code")]

    def __str__(self):
        return f"{self.name}({self.code})"


class ShopDictRel(BaseModel):
    """
    ShopDictRel 表 - 店铺与字典数据关联表
    """
    id = fields.IntField(pk=True, description="唯一标识")
    shop = fields.ForeignKeyField("models.Shops", related_name="dict_relations", on_delete=fields.CASCADE, description="店铺ID")
    dict_data = fields.ForeignKeyField("models.DictData", related_name="shop_relations", on_delete=fields.CASCADE, description="字典数据ID")

    class Meta:
        table = "shop_dict_rel"
        # 唯一约束：防止重复关联
        unique_together = [("shop_id", "dict_data_id")]

    def __str__(self):
        return f"ShopDictRel {self.id}: Shop {self.shop_id} -> DictData {self.dict_data_id}"