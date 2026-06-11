# image_dao.py — 图片数据访问

> 面向：业务逻辑层（Service）开发人员
> 文件位置：`dao/image_dao.py`
> 对应模型：`models/images.py` → `Images`

---

## 概述

`ImageDAO` 提供图片表的完整数据访问。`Images` 采用多态关联设计（`entity_type` + `entity_id`），不跨表 JOIN，级联清理在 DAO 层统一处理。

---

## 数据模型预览

### Images — 图片表

| 字段 | 类型 | 说明 |
|:---|:---|:---|
| id | BIGINT PK | 图片唯一标识 |
| url | VARCHAR(255) | 图片访问路径（相对路径或 CDN 地址） |
| entity_type | VARCHAR(32) | 关联实体类型，如 `shop`、`menu_item`、`shop_comment`、`comment_reply` |
| entity_id | BIGINT | 对应实体的主键 ID |
| file_size | INT (NULL) | 文件大小（字节） |
| width | INT (NULL) | 图片宽度（像素） |
| height | INT (NULL) | 图片高度（像素） |
| mime_type | VARCHAR(50) (NULL) | MIME 类型，如 `image/jpeg` |
| extra | JSON (NULL) | 扩展字段，存储 alt 文本等业务自定义信息 |
| uploader_id | INT (NULL) | 上传者用户 ID |

---

## 方法概览

### 基础 CRUD

| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `get_by_id(id)` | `int` | `Optional[Images]` | 按 ID 查询单张图片 |
| `create(url, entity_type, entity_id, ...)` | entity_type/entity_id 必填 | `Images` | 上传后写入图片记录 |
| `update(id, **kwargs)` | `int` + 字段 | `Optional[Images]` | 更新图片信息 |
| `delete(id)` | `int` | `bool` | 软删除单张图片（含 DictRel 级联清理） |

### 批量查询

| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `get_by_entity(entity_type, entity_id)` | entity_type + 实体ID | `List[Images]` | 查某实体的全部图片，按 id 升序 |
| `get_first_by_entity(entity_type, entity_id)` | entity_type + 实体ID | `Optional[Images]` | 取第一张作为封面图（最早上传） |

### 级联清理

| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `clear_entity_images(entity_type, entity_id)` | entity_type + 实体ID | `int` | 软删除某实体全部图片，返回清理条数 |

---

## 方法详述

### 基础 CRUD

---

#### `get_by_id(id)` — 按 ID 查询单张图片

根据图片 ID 查询一条图片记录。

**参数：**

| 参数名 | 类型 | 必填 | 说明 |
|:---|:---|:---:|:---|
| id | `int` | ✅ | 图片记录的主键 ID |

**返回：**

| 类型 | 说明 |
|:---|:---|
| `Optional[Images]` | 找到返回 Tortoise 模型实例；未找到或已软删除返回 `None` |

**使用示例：**

```python
img = await ImageDAO.get_by_id(42)
if img:
    print(img.url, img.entity_type, img.entity_id)
```

**业务场景：**
- 图片详情查询
- 删除/修改前校验图片是否存在

---

#### `create(url, entity_type, entity_id, file_size, width, height, mime_type, extra, uploader_id)` — 创建图片记录

新建一条图片记录，通常在文件上传成功后调用。

**参数：**

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|:---|:---|:---:|:---:|:---|
| url | `str` | ✅ | — | 图片访问路径 |
| entity_type | `str` | ✅ | — | 关联实体类型 |
| entity_id | `int` | ✅ | — |关联实体 ID |
| file_size | `Optional[int]` | ❌ | `None` | 文件大小（字节） |
| width | `Optional[int]` | ❌ | `None` | 图片宽度（像素） |
| height | `Optional[int]` | ❌ | `None` | 图片高度（像素） |
| mime_type | `Optional[str]` | ❌ | `None` | MIME 类型，如 `image/jpeg` |
| extra | `Optional[dict]` | ❌ | `None` | 扩展字段（alt 文本等） |
| uploader_id | `Optional[int]` | ❌ | `None` | 上传者用户 ID |

**返回：**

| 类型 | 说明 |
|:---|:---|
| `Images` | 返回新创建的 Tortoise 模型实例 |

**使用示例：**

```python
img = await ImageDAO.create(
    url="static/images/2026/05/abc.jpg",
    entity_type="shop",
    entity_id=shop.id,
    file_size=204800,
    width=1200,
    height=800,
    mime_type="image/jpeg",
    uploader_id=user.id,
)
```

**业务场景：**
- 文件上传成功后写入数据库记录
- 评论配图上传（需在评论创建后调用 `update()`修正 `entity_id`）

**实现逻辑（概述）：**
调用 `Images.create()` 插入数据库，返回新实例。

---

#### `update(id, **kwargs)` — 更新图片信息

更新指定图片记录的字段信息。

**参数：**

| 参数名 | 类型 | 必填 | 说明 |
|:---|:---|:---:|:---|
| id | `int` | ✅ | 图片 ID |
| **kwargs | 任意字段 | ✅ | 要更新的字段和值 |

**返回：**

| 类型 | 说明 |
|:---|:---|
| `Optional[Images]` | 更新成功返回更新后的实例；图片不存在或已软删除返回 `None` |

**使用示例：**

```python
# 评论创建成功后，将临时上传的图片关联到评论
updated = await ImageDAO.update(image_id, entity_type="shop_comment", entity_id=comment.id)
```

**业务场景：**
- 评论配图：上传时 entity_id 传入 shop_id，评论创建成功后修正为 comment_id
- 更新图片的 alt 文本等扩展信息

**实现逻辑（概述）：**
查询 `is_active=True` 记录，若存在则逐字段更新后保存。

---

#### `delete(id)` — 软删除单张图片

将指定图片标记为已删除（`is_active=False`），并同步清理该图片的 DictRel 标签关联记录。

**参数：**

| 参数名 | 类型 | 必填 | 说明 |
|:---|:---|:---:|:---|
| id | `int` | ✅ | 图片 ID |

**返回：**

| 类型 | 说明 |
|:---|:---|
| `bool` | 删除成功返回 `True`；图片不存在返回 `False` |

**使用示例：**

```python
ok = await ImageDAO.delete(image_id=99)
if not ok:
    raise ValueError("图片不存在")
```

**业务场景：**
- 用户删除自己上传的图片
- 管理员删除违规图片
- 删除时自动清理图片上的标签（DictRel）

**实现逻辑（概述）：**
查询 `is_active=True` 记录，若存在则调用 `DictRelDAO.clear_entity_dicts("image", id)` 清理多态标签关联，再置 `is_active=False` 后保存。

---

### 批量查询

---

#### `get_by_entity(entity_type, entity_id)` — 查某实体的全部图片

获取指定实体的所有图片，按 id 升序返回。

**参数：**

| 参数名 | 类型 | 必填 | 说明 |
|:---|:---|:---:|:---|
| entity_type | `str` | ✅ | 关联实体类型，如 `shop`、`menu_item`、`shop_comment` |
| entity_id | `int` | ✅ | 关联实体 ID |

**返回：**

| 类型 | 说明 |
|:---|:---|
| `List[Images]` | 该实体下所有图片的列表（按 id 升序） |

**使用示例：**

```python
# 获取店铺的全部图片
images = await ImageDAO.get_by_entity("shop", shop_id)
for img in images:
    print(img.url, img.width, img.height)

# 获取评论的配图
images = await ImageDAO.get_by_entity("shop_comment", comment_id)
```

**业务场景：**
- 店铺详情页相册列表
- 评论详情页配图展示

---

#### `get_first_by_entity(entity_type, entity_id)` — 取第一张图片作为封面图

获取指定实体的第一张图片（按 id 升序），即最早上传的那张。

**参数：**

| 参数名 | 类型 | 必填 | 说明 |
|:---|:---|:---:|:---|
| entity_type | `str` | ✅ | 关联实体类型 |
| entity_id | `int` | ✅ | 关联实体 ID |

**返回：**

| 类型 | 说明 |
|:---|:---|
| `Optional[Images]` | 找到返回第一张图片实例；无图片返回 `None` |

**使用示例：**

```python
# 店铺列表页封面
cover = await ImageDAO.get_first_by_entity("shop", shop_id)
if cover:
    print(cover.url)
```

**业务场景：**
- 店铺列表页每店的封面缩略图
- 菜品列表页每道菜的配图

**注意事项：**
- 按 id 升序取第一张，即最早上传的那张。如果业务需要"最新上传为封面"，需在 Service 层调用 `get_by_entity` 后取列表最后一项。

---

### 级联清理

---

#### `clear_entity_images(entity_type, entity_id)` — 软删除某实体的全部图片

将指定实体关联的所有图片软删除，用于实体删除时的级联清理。

**参数：**

| 参数名 | 类型 | 必填 | 说明 |
|:---|:---|:---:|:---|
| entity_type | `str` | ✅ | 关联实体类型 |
| entity_id | `int` | ✅ | 关联实体 ID |

**返回：**

| 类型 | 说明 |
|:---|:---|
| `int` | 被清理的图片记录条数 |

**使用示例：**

```python
# 删除店铺时清理全部图片
count = await ImageDAO.clear_entity_images("shop", shop_id)
print(f"已清理 {count} 张店铺图片")

# 删除评论时清理配图
count = await ImageDAO.clear_entity_images("shop_comment", comment_id)
```

**业务场景：**
- 删除店铺时，Service 层同步调用此方法清理该店铺下的所有图片
- 删除评论时清理评论配图

**实现逻辑（概述）：**
批量执行 `UPDATE ... SET is_active=False WHERE entity_type=X AND entity_id=Y AND is_active=True`，返回受影响行数。

---

## 典型用法汇总

```python
from dao import ImageDAO, DictRelDAO

# 1. 上传图片后写入记录
img = await ImageDAO.create(
    url="static/images/2026/05/abc.jpg",
    entity_type="shop",
    entity_id=shop.id,
    file_size=204800,
    width=1200,
    height=800,
    mime_type="image/jpeg",
    uploader_id=user.id,
)

# 2. 店铺详情页 — 获取全部图片
images = await ImageDAO.get_by_entity("shop", shop_id)
for img in images:
    print(img.url)

# 3. 店铺列表页 — 获取封面图
cover = await ImageDAO.get_first_by_entity("shop", shop_id)
if cover:
    print(cover.url)

# 4. 评论配图：先上传到临时店铺 ID，评论创建成功后修正
comment = await CommentDAO.create(...)
await ImageDAO.update(temp_image_id, entity_type="shop_comment", entity_id=comment.id)

# 5. 删除店铺 — 级联清理图片
await ImageDAO.clear_entity_images("shop", shop_id)

# 6. 删除图片（含清理标签关联）
ok = await ImageDAO.delete(image_id=99)
```

---

## 注意事项

1. **entity_type 取值约定**：`shop`、`menu_item`、`shop_comment`、`comment_reply`，旧值 `comment` 已废弃。
2. **`delete` 会同步清理 DictRel 标签关联**，图片可能被打了标签，删除时一并清理。
3. **封面图规则**：`get_first_by_entity` 按 id 升序取第一张，即最早上传的那张。如果业务需要"最新上传为封面"，需在 Service 层调 `get_by_entity` 后取列表最后一项。
4. **评论配图修正**：评论图片上传时 `entity_id` 传入 `shop_id`，评论创建成功后需调用 `update()` 将图片关联到评论。
5. **`clear_entity_images` 不验证实体是否存在**，调用方需确保在正确的时机调用（如实体删除后）。
6. **`uploader_id` 字段用于权限校验**：删除图片时需校验调用者是否为上传者或管理员。