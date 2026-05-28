import apiClient from './client';
import type { ApiResponse } from '../types/common';

export interface HistoryItem {
  id: number;
  operator_id: number;
  action: string;
  target_type: string;
  target_id: number;
  created_at: string;
}

/** 获取当前用户的浏览历史 */
export async function fetchHistory(page = 1, pageSize = 20): Promise<{ items: HistoryItem[]; total: number }> {
  const res = await apiClient.get<ApiResponse<{ items: HistoryItem[]; total: number }>>('/users/me/history', {
    params: { page, page_size: pageSize },
  });
  return res.data.data;
}
