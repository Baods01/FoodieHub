/** 收藏项 — 对齐后端 FavoriteResponse */
export interface FavoriteItem {
  id: number;
  shop_id: number;
  shop_name: string | null;
  shop_cover: string | null;
  created_at: string;
}
