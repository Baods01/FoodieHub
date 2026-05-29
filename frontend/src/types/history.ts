/** 浏览历史项 — 对齐后端 ViewHistoryItem */
export interface HistoryItem {
  id: number;
  shop_id: number;
  shop_name: string;
  shop_cover: string | null;
  region: string | null;
  viewed_at: string;
}
