// 浏览历史接口
// 浏览历史已从独立接口移除，改为通过 OperationLog 记录。
// 如需获取用户浏览历史，未来可通过以下方式：
// GET /users/me/history（待开发）

export interface HistoryItem {
  shop_id: number;
  shop_name: string;
  viewed_at: string;
}
