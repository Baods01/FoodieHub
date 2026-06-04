# comment_service.py — 评论业务逻辑

> 面向：Router 层开发人员
> 文件位置：`services/comment_service.py`

---

## 概述

CommentService 提供评论区的完整操作：一级评论 CRUD、二级回复、点赞同步。

---

## 方法列表

| 方法 | 参数 | 返回 | 说明 |
|:---|:---|:---|:---|
| `create(shop_id, user_id, content, image_id)` | image_id 可选 | `dict` | ⭐ 发表评论（支持附带一张图片） |
| `list_by_shop(shop_id, page, page_size)` | | `dict` | ⭐ 某店铺的评论列表（含图片） |
| `list_by_user(user_id, page, page_size)` | | `dict` | 某用户的评论列表 |
| `update(comment_id, content)` | | `Optional[dict]` | 更新评论 |
| `delete(comment_id)` | | `bool` | 删除评论 |
| `create_reply(comment_id, user_id, content, reply_to_user_id)` | reply_to 可选 | `dict` | ⭐ 回复评论 |
| `list_replies(comment_id)` | | `list` | 某评论的全部回复 |
| `delete_reply(reply_id)` | | `bool` | |
| `toggle_like(user_id, comment_id)` | | `dict` | ⭐ 点赞/取消赞，返回 `{is_liked, like_count}` |

---

## 评论图片说明

一级评论可附带一张图片，流程如下：

1. **前端上传**：用户选图后调用 `POST /images/upload`，entity_type=`"shop_comment"`，entity_id 传 `shop_id`（临时）
2. **后端修正**：评论创建成功后，`CommentService.create` 会调用 `ImageDAO.update(image_id, entity_id=comment_id)` 将图片绑定到评论
3. **列表返回**：`list_by_shop` 调用 `ImageDAO.get_by_entity("shop_comment", comment_id)` 取图片 URL

---

## 典型用法

```python
# 发表评论（含图片）
c = await CommentService.create(shop_id, user.id, "好吃！", image_id=123)

# 获取评论列表
comments = await CommentService.list_by_shop(shop_id)
for c in comments["items"]:
    img_url = c.get("image")  # 评论图片

# 点赞
result = await CommentService.toggle_like(user.id, comment_id)
```