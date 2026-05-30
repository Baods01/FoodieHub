import apiClient from './client';
import type { ApiResponse } from '../types/common';

export interface HistoryItem {
  id: number;
  shop_id: number;
  shop_name: string;
  shop_cover: string | null;
  region: string | null;
  viewed_at: string;
}

/** 获取当前用户的浏览历史 */
export async function fetchHistory(page = 1, pageSize = 20): Promise<{ items: HistoryItem[]; total: number; has_more: boolean }> {
  const res = await apiClient.get<ApiResponse<{ items: HistoryItem[]; total: number; has_more: boolean }>>('/users/me/history', {
    params: { page, page_size: pageSize },
  });
  return res.data.data;
}

/** 删除单条浏览历史 */
export async function deleteHistory(historyId: number): Promise<void> {
  await apiClient.delete(`/users/me/history/${historyId}`);
}

/** 清空所有浏览历史 */
export async function clearHistory(): Promise<number> {
  const res = await apiClient.delete<ApiResponse<{ deleted_count: number }>>('/users/me/history/clear');
  return res.data.data.deleted_count;
}
