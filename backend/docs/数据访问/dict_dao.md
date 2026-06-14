# dict_dao.py — 字典体系数据访问

> 面向：业务逻辑层（Service）开发人员
> 文件位置：`dao/dict_dao.py`
> 对应模型：`models/dict.py` → `DictTypes` / `DictData` / `DictRel`

---

## 概述

`dict_dao` 提供字典体系三张表的完整数据访问：

- **`DictTypeDAO`** — 字典类型表（DictTypes），定义标签分类
- **`DictDataDAO`** — 字典数据表（DictData），具体的标签值
- **`DictRelDAO`** — 字典关联表（DictRel），将标签多态关联到任意实体

所有方法均不包含业务语义（如"品类""区域"），调用方传入 ID 或名称，返回原始数据。

---

## 数据模型预览

### DictTypes — 字典类型表

| 字段 | 类型 | 说明 |
|:---|:---|:---|
| id | INT PK | 自增主键 |
| name | VARCHAR(50) UNIQUE | 类型名称（业务唯一标识），如 `"品类"` / `"区域"` |
| target_table | VARCHAR(50) | 所属业务表名，标记这个字典类型属于哪张表 |
| description | VARCHAR(255) NULL | 类型描述 |
| sort_order | INT | 类型间的排序顺序 |
| is_active | BOOLEAN | 软删除标记（继承自 BaseModel） |

### DictData — 字典数据表

| 字段 | 类型 | 说明 |
|:---|:---|:---|
| id | INT PK | 自增主键 |
| dict_type | FK → DictTypes | 所属字典类型 |
| name | VARCHAR(50) | 标签名称，如 `"火锅"` / `"华农西门"`。同一类型下唯一 |
| sort_order | INT | 同一类型内的排序 |
| is_default | BOOLEAN | 是否为默认选中值 |
| extra | JSON NULL | 扩展字段（图标、颜色等），预留 |
| is_active | BOOLEAN | 软删除标记 |

### DictRel — 字典关联表（多态）

| 字段 | 类型 | 说明 |
|:---|:---|:---|
| id | INT PK | 自增主键 |
| entity_type | VARCHAR(32) | 关联实体类型，如 `"shop"` / `"user"` / `"feedback"` |
| entity_id | BIGINT | 关联实体主键 ID |
| dict_data | FK → DictData | 字典数据 ID |
| is_active | BOOLEAN | 软删除标记 |

**唯一约束：** `(entity_type, entity_id, dict_data_id)` — 防止重复关联。
**索引：** `(entity_type, entity_id)` — 快速查某个实体的全部标签。

---

## 方法概览

### DictTypeDAO — 字典类型

| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `get_by_id(id)` | `int` | `Optional[DictTypes]` | 按 ID 查询 |
| `get_by_name(name)` | `str` | `Optional[DictTypes]` | 按名称精确查询（唯一） |
| `get_all()` | — | `List[DictTypes]` | 全量，按 sort_order 排序 |
| `create(name, target_table, description, sort_order)` | `description`/`sort_order` 可选 | `DictTypes` | 创建新字典类型 |
| `update(id, **kwargs)` | `id` + 任意字段 | `Optional[DictTypes]` | 更新，不存在返回 None |
| `delete(id)` | `int` | `bool` | 软删除 |

### DictDataDAO — 字典数据

| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `get_by_id(id)` | `int` | `Optional[DictData]` | 按 ID 查询 |
| `get_by_dict_type(dict_type_id)` | `int` | `List[DictData]` | 某类型下的全部数据项 |
| `get_by_type_name(type_name)` | `str` | `List[DictData]` | ⭐ 按类型名称批量查 |
| `get_by_name(type_name, data_name)` | `str` + `str` | `Optional[DictData]` | 精确定位某类型下某名称 |
| `create(dict_type_id, name, sort_order, is_default, extra)` | `sort_order`/`is_default`/`extra` 可选 | `DictData` | 创建字典数据 |
| `update(id, **kwargs)` | `id` + 任意字段 | `Optional[DictData]` | 更新，不存在返回 None |
| `delete(id)` | `int` | `bool` | 软删除 |

### DictRelDAO — 字典关联

| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `get_entity_dicts(entity_type, entity_id)` | `str` + `int` | `list[dict]` | ⭐ 查某实体的全部标签（结构化） |
| `add_dict_to_entity(entity_type, entity_id, dict_data_id)` | — | `DictRel` | 打标签（幂等） |
| `remove_dict_from_entity(entity_type, entity_id, dict_data_id)` | — | `bool` | 移除标签（软删除） |
| `clear_entity_dicts(entity_type, entity_id)` | `str` + `int` | `int` | 清除实体的全部标签 |
| `get_entities_by_dict(dict_data_id)` | `int` | `List[int]` | 反向查询：某标签下的所有 entity_id |

---

## 方法详述

### DictTypeDAO — 字典类型

---

#### `get_by_id(id)` — 按 ID 查询字典类型

根据字典类型 ID 查询一条记录。

**参数：**

| 参数名 | 类型 | 必填 | 说明 |
|:---|:---|:---:|:---|
| id | `int` | ✅ | 字典类型主键 ID |

**返回：**

| 类型 | 说明 |
|:---|:---|
| `Optional[DictTypes]` | 找到返回 Tortoise 模型实例；未找到或已软删除返回 `None` |

**使用示例：**

```python
dtype = await DictTypeDAO.get_by_id(1)
if dtype:
    print(dtype.name, dtype.target_table)
```

---

#### `get_by_name(name)` — 按名称精确查询字典类型

根据字典类型的 `name` 字段精确查询。

**参数：**

| 参数名 | 类型 | 必填 | 说明 |
|:---|:---|:---:|:---|
| name | `str` | ✅ | 字典类型名称，如 `"品类"` / `"区域"` |

**返回：**

| 类型 | 说明 |
|:---|:---|
| `Optional[DictTypes]` | 找到返回实例；未找到返回 `None` |

**使用示例：**

```python
dtype = await DictTypeDAO.get_by_name("品类")
if dtype:
    print(dtype.id, dtype.target_table)  # id=1, target_table="shops"
```

**业务场景：**
- 校验某个字典类型是否存在
- 根据名称获取类型后进一步查询其下的数据项

---

#### `get_all()` — 获取全部字典类型

查询所有活跃的字典类型，按 `sort_order` 升序排列。

**参数：** 无

**返回：**

| 类型 | 说明 |
|:---|:---|
| `List[DictTypes]` | 所有活跃字典类型的列表 |

**使用示例：**

```python
all_types = await DictTypeDAO.get_all()
for dtype in all_types:
    print(dtype.name, dtype.target_table)
# 品类 → shops, 区域 → shops, 就餐方式 → shops
```

**业务场景：**
- 前端初始化字典类型筛选器
- 管理后台展示所有字典分类

---

#### `create(name, target_table, description, sort_order)` — 创建字典类型

新建一个字典类型。

**参数：**

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|:---|:---|:---:|:---:|:---|
| name | `str` | ✅ | — | 类型名称（唯一标识），如 `"品类"` |
| target_table | `str` | ✅ | — | 所属业务表名，如 `"shops"` |
| description | `Optional[str]` | ❌ | `None` | 类型描述 |
| sort_order | `int` | ❌ | `0` | 排序序号 |

**返回：**

| 类型 | 说明 |
|:---|:---|
| `DictTypes` | 返回新创建的 Tortoise 模型实例 |

**使用示例：**

```python
dtype = await DictTypeDAO.create(
    name="就餐方式",
    target_table="shops",
    description="堂食、自取、外卖等",
    sort_order=3,
)
```

---

#### `update(id, **kwargs)` — 更新字典类型

更新指定字典类型的任意字段。

**参数：**

| 参数名 | 类型 | 必填 | 说明 |
|:---|:---|:---:|:---|
| id | `int` | ✅ | 字典类型 ID |
| **kwargs | 任意字段名 | ❌ | 要更新的字段及新值 |

**返回：**

| 类型 | 说明 |
|:---|:---|
| `Optional[DictTypes]` | 更新成功返回更新后的实例；不存在返回 `None` |

**使用示例：**

```python
updated = await DictTypeDAO.update(1, description="更新后的描述", sort_order=5)
```

**实现逻辑（概述）：**
查询 `is_active=True` 记录，若存在则逐字段更新后保存。

---

#### `delete(id)` — 软删除字典类型

将指定字典类型标记为已删除（`is_active=False`）。

**参数：**

| 参数名 | 类型 | 必填 | 说明 |
|:---|:---|:---:|:---|
| id | `int` | ✅ | 字典类型 ID |

**返回：**

| 类型 | 说明 |
|:---|:---|
| `bool` | 删除成功返回 `True`；不存在返回 `False` |

**注意事项：**
- 软删除字典类型后，该类型下的所有 DictData 和 DictRel 记录**不会被级联软删除**
- 若需彻底清理，需在 Service 层自行处理 DictData 和 DictRel 的软删除

---

### DictDataDAO — 字典数据

---

#### `get_by_id(id)` — 按 ID 查询字典数据

根据字典数据 ID 查询一条记录。

**参数：**

| 参数名 | 类型 | 必填 | 说明 |
|:---|:---|:---:|:---|
| id | `int` | ✅ | 字典数据主键 ID |

**返回：**

| 类型 | 说明 |
|:---|:---|
| `Optional[DictData]` | 找到返回实例；未找到或已软删除返回 `None` |

---

#### `get_by_dict_type(dict_type_id)` — 某类型下的全部字典数据

获取指定字典类型下所有活跃的数据项，按 `sort_order` 排序。

**参数：**

| 参数名 | 类型 | 必填 | 说明 |
|:---|:---|:---:|:---|
| dict_type_id | `int` | ✅ | 字典类型 ID |

**返回：**

| 类型 | 说明 |
|:---|:---|
| `List[DictData]` | 该类型下所有活跃数据项列表 |

**使用示例：**

```python
items = await DictDataDAO.get_by_dict_type(dict_type_id=1)
for item in items:
    print(item.name, item.is_default)
```

**业务场景：**
- 前端下拉框选项渲染
- 获取某类型下所有可选标签值

---

#### `get_by_type_name(type_name)` — 按类型名称批量查询字典数据

按字典类型名称（如 `"品类"` / `"区域"`）查询该类型下所有活跃数据项，按 `sort_order` 排序。

**参数：**

| 参数名 | 类型 | 必填 | 说明 |
|:---|:---|:---:|:---|
| type_name | `str` | ✅ | 字典类型名称，如 `"品类"` |

**返回：**

| 类型 | 说明 |
|:---|:---|
| `List[DictData]` | 该类型下所有活跃数据项列表 |

**使用示例：**

```python
# 前端初始化品类下拉框
categories = await DictDataDAO.get_by_type_name("品类")
# [DictData(id=1, name="火锅"), DictData(id=2, name="烧烤"), ...]

# 前端初始化区域下拉框
areas = await DictDataDAO.get_by_type_name("区域")
# [DictData(id=5, name="华农西门"), DictData(id=6, name="泰山区"), ...]
```

**业务场景：**
- 前端表单初始化标签选择器（品类、区域、就餐方式）
- 无需先查 DictType ID，直接按名称查询

---

#### `get_by_name(type_name, data_name)` — 精确定位字典数据

在指定字典类型下，通过类型名称 + 数据名称精确定位一条记录。

**参数：**

| 参数名 | 类型 | 必填 | 说明 |
|:---|:---|:---:|:---|
| type_name | `str` | ✅ | 字典类型名称，如 `"品类"` |
| data_name | `str` | ✅ | 字典数据名称，如 `"火锅"` |

**返回：**

| 类型 | 说明 |
|:---|:---|
| `Optional[DictData]` | 找到返回实例；未找到返回 `None` |

**使用示例：**

```python
hotpot = await DictDataDAO.get_by_name("品类", "火锅")
if hotpot:
    print(hotpot.id)  # 精确定位到某个具体的 DictData
```

**业务场景：**
- 创建/更新店铺时，校验某个标签值是否已存在
- 通过名称反查 ID（如 `"火锅"` → id=5）

---

#### `create(dict_type_id, name, sort_order, is_default, extra)` — 创建字典数据

在指定字典类型下新建一条字典数据。

**参数：**

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|:---|:---|:---:|:---:|:---|
| dict_type_id | `int` | ✅ | — | 所属字典类型 ID |
| name | `str` | ✅ | — | 数据名称，如 `"火锅"` |
| sort_order | `int` | ❌ | `0` | 排序序号 |
| is_default | `bool` | ❌ | `False` | 是否为默认选中值 |
| extra | `Optional[dict]` | ❌ | `None` | 扩展字段 JSON（如 `{icon: "🍲"}`） |

**返回：**

| 类型 | 说明 |
|:---|:---|
| `DictData` | 返回新创建的 Tortoise 模型实例 |

**使用示例：**

```python
data = await DictDataDAO.create(
    dict_type_id=1,
    name="火锅",
    sort_order=1,
    is_default=True,
    extra={"icon": "🍲", "color": "#ff0000"},
)
```

---

#### `update(id, **kwargs)` — 更新字典数据

更新指定字典数据的任意字段。

**参数：**

| 参数名 | 类型 | 必填 | 说明 |
|:---|:---|:---:|:---|
| id | `int` | ✅ | 字典数据 ID |
| **kwargs | 任意字段名 | ❌ | 要更新的字段及新值 |

**返回：**

| 类型 | 说明 |
|:---|:---|
| `Optional[DictData]` | 更新成功返回更新后的实例；不存在返回 `None` |

**使用示例：**

```python
updated = await DictDataDAO.update(5, name="更新后的名称", is_default=True)
```

**实现逻辑（概述）：**
查询 `is_active=True` 记录，若存在则逐字段更新后保存。

---

#### `delete(id)` — 软删除字典数据

将指定字典数据标记为已删除（`is_active=False`）。

**参数：**

| 参数名 | 类型 | 必填 | 说明 |
|:---|:---|:---:|:---|
| id | `int` | ✅ | 字典数据 ID |

**返回：**

| 类型 | 说明 |
|:---|:---|
| `bool` | 删除成功返回 `True`；不存在返回 `False` |

**注意事项：**
- 软删除 DictData 后，**不会级联软删除相关的 DictRel 记录**
- 业务层如需完全清理，需同步处理 DictRel

---

### DictRelDAO — 字典关联（多态）

---

#### `get_entity_dicts(entity_type, entity_id)` — 查某实体的全部标签（结构化）

获取指定实体的所有活跃标签，返回带类型名称的结构化数据。

**参数：**

| 参数名 | 类型 | 必填 | 说明 |
|:---|:---|:---:|:---|
| entity_type | `str` | ✅ | 实体类型，如 `"shop"` / `"user"` / `"feedback"` |
| entity_id | `int` | ✅ | 实体主键 ID |

**返回：**

| 字段 | 类型 | 说明 |
|:---|:---|:---|
| `dict_type_name` | `str` | 字典类型名称，如 `"品类"` |
| `dict_data_id` | `int` | 字典数据 ID |
| `dict_data_name` | `str` | 字典数据名称，如 `"火锅"` |

**返回示例：**

```python
[
    {"dict_type_name": "品类", "dict_data_id": 5, "dict_data_name": "火锅"},
    {"dict_type_name": "区域", "dict_data_id": 9, "dict_data_name": "华农西门"},
]
```

**使用示例：**

```python
# 获取店铺的全部标签（前端详情页展示）
tags = await DictRelDAO.get_entity_dicts("shop", shop_id=123)
for tag in tags:
    print(f"{tag['dict_type_name']}: {tag['dict_data_name']}")
# 品类: 火锅
# 区域: 华农西门
```

**业务场景：**
- 店铺详情页标签展示
- 前端筛选器回填已选标签

**实现逻辑（概述）：**
查询 `entity_type + entity_id` 的所有 DictRel，JOIN DictData 和 DictType，过滤已软删除的 DictData 后组装返回。

**注意事项：**
- 自动过滤已软删除的 DictData 和 DictType，不会返回孤儿数据

---

#### `add_dict_to_entity(entity_type, entity_id, dict_data_id)` — 为实体打标签（幂等）

将某个标签关联到指定实体。若关联已存在（无论 is_active 状态），会复用已有记录。

**参数：**

| 参数名 | 类型 | 必填 | 说明 |
|:---|:---|:---:|:---|
| entity_type | `str` | ✅ | 实体类型，如 `"shop"` |
| entity_id | `int` | ✅ | 实体主键 ID |
| dict_data_id | `int` | ✅ | 字典数据 ID |

**返回：**

| 类型 | 说明 |
|:---|:---|
| `DictRel` | 返回新创建或已恢复的 DictRel 实例 |

**使用示例：**

```python
# 给店铺打标签
rel = await DictRelDAO.add_dict_to_entity(
    entity_type="shop",
    entity_id=shop_id,
    dict_data_id=5,  # 火锅
)
```

**幂等行为说明：**
- 若该关联**不存在** → 创建新记录
- 若该关联已存在且 `is_active=False` → 恢复为 `is_active=True`，复用记录
- 若该关联已存在且 `is_active=True` → 直接返回现有记录

**业务场景：**
- 创建/更新店铺时保存标签选择
- 重复调用不会产生重复记录

---

#### `remove_dict_from_entity(entity_type, entity_id, dict_data_id)` — 移除实体的某个标签

将指定实体的某个标签关联标记为软删除（`is_active=False`）。

**参数：**

| 参数名 | 类型 | 必填 | 说明 |
|:---|:---|:---:|:---|
| entity_type | `str` | ✅ | 实体类型，如 `"shop"` |
| entity_id | `int` | ✅ | 实体主键 ID |
| dict_data_id | `int` | ✅ | 字典数据 ID |

**返回：**

| 类型 | 说明 |
|:---|:---|
| `bool` | 移除成功返回 `True`；关联不存在返回 `False` |

**使用示例：**

```python
ok = await DictRelDAO.remove_dict_from_entity(
    entity_type="shop",
    entity_id=shop_id,
    dict_data_id=5,
)
```

**业务场景：**
- 编辑店铺时取消某个标签
- 删除实体时清理其全部标签（用 `clear_entity_dicts` 更高效）

---

#### `clear_entity_dicts(entity_type, entity_id)` — 清除实体的全部标签

将指定实体的所有标签关联全部软删除，通常在实体被删除时调用。

**参数：**

| 参数名 | 类型 | 必填 | 说明 |
|:---|:---|:---:|:---|
| entity_type | `str` | ✅ | 实体类型，如 `"shop"` |
| entity_id | `int` | ✅ | 实体主键 ID |

**返回：**

| 类型 | 说明 |
|:---|:---|
| `int` | 被清理的 DictRel 记录条数 |

**使用示例：**

```python
count = await DictRelDAO.clear_entity_dicts("shop", shop_id=123)
print(f"已清理 {count} 条标签关联")
```

**业务场景：**
- 删除店铺时，Service 层同步调用此方法清理该店铺的所有标签关联
- 用户注销时清理该用户的标签关联

**实现逻辑（概述）：**
批量执行 `UPDATE ... SET is_active=False WHERE entity_type=X AND entity_id=Y AND is_active=True`，返回受影响行数。

---

#### `get_entities_by_dict(dict_data_id)` — 反向查询：某标签下的所有实体 ID

根据字典数据 ID，反向查询所有关联到该标签的实体 ID列表。

**参数：**

| 参数名 | 类型 | 必填 | 说明 |
|:---|:---|:---:|:---|
| dict_data_id | `int` | ✅ | 字典数据 ID |

**返回：**

| 类型 | 说明 |
|:---|:---|
| `List[int]` | 所有关联到该标签的 entity_id 列表 |

**返回示例：**

```python
entity_ids = await DictRelDAO.get_entities_by_dict(dict_data_id=5)
# [101, 205, 318, ...]  所有关联了"火锅"标签的店铺 ID
```

**业务场景：**
- 前端标签筛选：点击"火锅"标签，查询所有关联了"火锅"的店铺
- 管理后台统计某标签下的实体数量

**注意事项：**
- 返回的是 entity_id 列表，调用方需自行根据 entity_type 过滤
- 不做任何 FK 校验，多态设计无外键约束，上层需确保传入合法的实体 ID

---

## 典型用法汇总

```python
from dao import DictTypeDAO, DictDataDAO, DictRelDAO

# 1. 前端初始化 — 获取所有字典类型
all_types = await DictTypeDAO.get_all()

# 2. 前端初始化 — 品类下拉框
categories = await DictDataDAO.get_by_type_name("品类")
# [DictData(id=1, name="火锅"), DictData(id=2, name="烧烤"), ...]

# 3. 前端初始化 — 区域下拉框
areas = await DictDataDAO.get_by_type_name("区域")
# [DictData(id=5, name="华农西门"), DictData(id=6, name="泰山区"), ...]

# 4. 创建店铺时 — 保存标签
for dict_data_id in selected_tag_ids:
    await DictRelDAO.add_dict_to_entity("shop", shop_id, dict_data_id)

# 5. 店铺详情页 — 展示标签
tags = await DictRelDAO.get_entity_dicts("shop", shop_id=123)
# [{"dict_type_name": "品类", "dict_data_id": 5, "dict_data_name": "火锅"}, ...]

# 6. 编辑店铺时 — 取消某个标签
await DictRelDAO.remove_dict_from_entity("shop", shop_id, dict_data_id=5)

# 7. 删除店铺时 — 清理全部标签关联
count = await DictRelDAO.clear_entity_dicts("shop", shop_id=123)

# 8. 前端标签筛选 — 查询某标签下的所有店铺
shop_ids = await DictRelDAO.get_entities_by_dict(dict_data_id=5)
# [101, 205, 318, ...]
```

---

## 注意事项

1. **DictRelDAO 不校验 entity_id 是否存在**。多态设计无 FK 约束，上层调用方需确保传入合法的实体 ID。
2. **`add_dict_to_entity` 是幂等的**：若关联已存在且 `is_active=False`，会自动恢复而非创建新记录。
3. **`add_dict_to_entity` 和 `remove_dict_from_entity` 不会更新任何冗余 count 字段**（如 Shops 表无"标签数"字段）。
4. **`get_entity_dicts` 自动过滤已软删除的 DictData 和 DictTypes**，不会返回孤儿数据或空类型名。
5. **软删除 DictType 或 DictData不会级联软删除相关的 DictRel 记录**，业务层需自行处理清理逻辑。
6. **`get_entities_by_dict` 返回的是 entity_id 列表**，不包含实体类型信息，调用方需自行根据 entity_type 过滤或校验。