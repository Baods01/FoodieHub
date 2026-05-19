import type { ShopCardData } from './shop';

/** 收藏项 = 店铺卡片数据 + 收藏时间 */
export interface FavoriteItem extends ShopCardData {
  favoritedAt: string; // ISO date string
}
