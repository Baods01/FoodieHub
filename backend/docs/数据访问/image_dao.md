# image_dao.py — 图片数据访问

> 面向：业务逻辑层（Service）开发人员
> 文件位置：`dao/image_dao.py`

---

## 概述

image_dao 提供 Images 表的完整访问。Images 采用多态关联（entity_type + entity_id），不跨表 JOIN。

---

## 方法列表

### 基础 CRUD

| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `get_by_id(id)` | id | `Optional[Images]` | 单张详情 |
| `create(url, entity_type, entity_id, file_size, width, height, mime_type, extra)` | url + entity 必填，其余可选 | `Images` | ⭐ 上传后写入 |
| `update(id, **kwargs)` | id + 字段 | `Optional[Images]` | 更新图片信息 |
| `delete(id)` | id | `bool` | 软删除单张 |

### 批量查询

| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `get_by_entity(entity_type, entity_id)` | `"shop"`, 实体ID | `List[Images]` | ⭐ 查某实体的全部图片，按 id 升序 |
| `get_first_by_entity(entity_type, entity_id)` | 同上 | `Optional[Images]` | ⭐ 取第一张作为封面图 |

### 级联清理

| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `clear_entity_images(entity_type, entity_id)` | entity_type + id | `int` | 软删除某实体全部图片，返回删除数 |

---

## 典型用法

```python
from dao import ImageDAO

# 上传图片后写入
img = await ImageDAO.create(
    url="static/images/2026/05/abc.jpg",
    entity_type="shop",
    entity_id=shop.id,
    file_size=204800,
    width=1200,
    height=800,
    mime_type="image/jpeg",
)

# 取店铺封面（首页列表）
cover = await ImageDAO.get_first_by_entity("shop", shop_id)

# 取评论配图（详情页评论区）
images = await ImageDAO.get_by_entity("shop_comment", comment_id)

# 删除店铺时清理图片
await ImageDAO.clear_entity_images("shop", shop_id)
```

---

## 注意事项

1. **entity_type 取值约定**：`"shop"`、`"menu_item"`、`"shop_comment"`（不要用旧 `"comment"`，旧模型已删除）
2. **封面图规则**：`get_first_by_entity` 按 id 升序取第一张，即最早上传的那张。如果业务需要"最新上传为封面"，需在 Service 层调 `get_by_entity` 后取最后一张。
3. **`clear_entity_images` 不验证实体是否存在**，调用方需确保在正确的时机调用（如实体删除后）。
