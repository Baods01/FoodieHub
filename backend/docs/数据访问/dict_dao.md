# dict_dao.py — 字典体系数据访问

> 面向：业务逻辑层（Service）开发人员
> 文件位置：`dao/dict_dao.py`

---

## 概述

dict_dao 提供字典三大模型的全部基础访问方法：
DictType（字典类型）、DictData（字典数据）、DictRel（字典关联）。

不涉及任何业务语义（如"品类""区域"），调用方传入 ID 或名称，返回原始数据。

---

## DictTypeDAO — 字典类型

| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `get_by_id(id)` | id: int | `Optional[DictTypes]` | 按 ID 查 |
| `get_by_name(name)` | name: str | `Optional[DictTypes]` | 按名称查（唯一） |
| `get_all()` | — | `List[DictTypes]` | 全量，按 sort_order 排序 |
| `create(name, target_table, description, sort_order)` | 后两个可选 | `DictTypes` | 创建新字典类型 |
| `update(id, **kwargs)` | id + 要改的字段 | `Optional[DictTypes]` | 更新，不存在返回 None |
| `delete(id)` | id: int | `bool` | 软删除 |

**典型用法：**
```python
from dao import DictTypeDAO

# 查所有字典类型（前端筛选器初始化）
types = await DictTypeDAO.get_all()

# 检查某个类型是否存在
if await DictTypeDAO.get_by_name("品类"):
    ...
```

---

## DictDataDAO — 字典数据

| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `get_by_id(id)` | id: int | `Optional[DictData]` | 按 ID 查 |
| `get_by_dict_type(dict_type_id)` | 类型 ID | `List[DictData]` | 某类型下的全部数据项 |
| `get_by_type_name(type_name)` | 类型名称如"品类" | `List[DictData]` | ⭐ 按类型名称批量查 |
| `get_by_name(type_name, data_name)` | 类型名称 + 数据名称 | `Optional[DictData]` | 精确定位一项 |
| `create(dict_type_id, name, ...)` | 必填：类型 ID + 名称 | `DictData` | 创建字典数据 |
| `update(id, **kwargs)` | id + 字段 | `Optional[DictData]` | 更新 |
| `delete(id)` | id: int | `bool` | 软删除 |

**典型用法：**
```python
from dao import DictDataDAO

# 获取所有品类选项（前端下拉框）
categories = await DictDataDAO.get_by_type_name("品类")

# 精确定位
hotpot = await DictDataDAO.get_by_name("品类", "火锅")
```

---

## DictRelDAO — 字典关联

| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `get_entity_dicts(entity_type, entity_id)` | `"shop"`, 店铺ID | `list[dict]` | ⭐ 查某实体的全部标签，返回结构化数据 |
| `add_dict_to_entity(entity_type, entity_id, dict_data_id)` | 同上 | `DictRel` | 打标签（已有则恢复 is_active） |
| `remove_dict_from_entity(entity_type, entity_id, dict_data_id)` | 同上 | `bool` | 移除标签 |
| `clear_entity_dicts(entity_type, entity_id)` | entity_type + id | `int` | 清除全部标签 |
| `get_entities_by_dict(dict_data_id)` | 字典数据 ID | `List[int]` | 反向查：某标签下所有 entity_id |

**`get_entity_dicts` 返回格式：**
```python
[
    {"dict_type_name": "品类", "dict_data_id": 5, "dict_data_name": "火锅"},
    {"dict_type_name": "区域", "dict_data_id": 9, "dict_data_name": "华农西门"},
]
```
此结构包含类型名和数据名，前端筛选器渲染、详情页展示均够用，Service 无需二次拼装。

**典型用法：**
```python
from dao import DictRelDAO

# 获取店铺的全部标签
tags = await DictRelDAO.get_entity_dicts("shop", shop_id=123)

# 给店铺打标签
await DictRelDAO.add_dict_to_entity("shop", shop_id, dict_data_id=5)
```

---

## 注意事项

1. **DictRelDAO 不校验 entity_id 是否存在**。多态设计无 FK 约束，上层需确保传入合法的实体 ID。
2. **`add_dict_to_entity` 是幂等的**：如果该关联已存在且 is_active=False，会恢复而非创建新记录。
3. **`add_dict_to_entity` 和 `remove_dict_from_entity` 不会更新任何 count 字段**（如 shops 表没有"标签数"字段）。
4. **`get_entity_dicts` 自动过滤已软删除的 DictData 和 DictTypes**，不会返回孤儿数据。
