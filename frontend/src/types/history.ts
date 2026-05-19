import type { ShopCardData } from './shop';

/** 浏览历史项 = 店铺卡片数据 + 浏览时间 */
export interface HistoryItem extends ShopCardData {
  viewedAt: string; // ISO date string
}
