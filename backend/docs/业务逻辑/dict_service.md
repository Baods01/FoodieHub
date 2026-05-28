# dict_service.py — 字典业务逻辑

> 面向：Router 层开发人员
> 文件位置：`services/dict_service.py`

---

## 概述

DictService 包装 DictTypeDAO、DictDataDAO、DictRelDAO，提供字典体系的全套操作。纯透传，不做业务判断。

---

## 方法列表

### DictType

| 方法 | 参数 | 返回 |
|:---|:---|:---|
| `get_type_by_id(id)` | int | `Optional[DictTypeResponse]` |
| `get_type_by_name(name)` | str | `Optional[DictTypeResponse]` |
| `list_types()` | — | `list[DictTypeResponse]` |
| `list_types_with_children()` | — | `list[DictTypeWithChildrenResponse]` |
| `create_type(name, target_table, ...)` | name, target_table 必填 | `DictTypeResponse` |
| `update_type(id, **kwargs)` | id + 字段 | `Optional[DictTypeResponse]` |
| `delete_type(id)` | int | `bool` |

### DictData

| 方法 | 参数 | 返回 |
|:---|:---|:---|
| `get_data_by_id(id)` | int | `Optional[DictDataResponse]` |
| `list_data_by_type(dict_type_id)` | int | `list[DictDataResponse]` |
| `list_data_by_type_name(type_name)` | str | `list[DictDataResponse]` |
| `create_data(dict_type_id, name, ...)` | type_id + name 必填 | `DictDataResponse` |
| `update_data(id, **kwargs)` | id + 字段 | `Optional[DictDataResponse]` |
| `delete_data(id)` | int | `bool` |

### DictRel

| 方法 | 参数 | 返回 |
|:---|:---|:---|
| `get_entity_dicts(entity_type, entity_id)` | `"shop"`, id | `list[dict]` |
| `add_dict_to_entity(entity_type, entity_id, dict_data_id)` | — | `None` |
| `remove_dict_from_entity(entity_type, entity_id, dict_data_id)` | — | `bool` |
| `clear_entity_dicts(entity_type, entity_id)` | — | `int` |

---

## 注意事项

1. `list_data_by_type_name` 是最常用的方法——前端下拉框预加载"品类"选项时调用。
2. DictRel 方法不校验 entity_id 是否存在，调用方需保证。
