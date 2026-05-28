import apiClient from './client';
import type { ApiResponse } from '../types/common';

export interface ActivityItem {
  id: number;
  user_id: number;
  type: string;
  target_id: number;
  target_type: string;
  content: string | null;
  shop_id: number | null;
  created_at: string;
}

/** 获取用户动态列表 */
export async function fetchActivities(userId: number | 'me', page = 1, pageSize = 20): Promise<{ items: ActivityItem[]; total: number }> {
  const url = userId === 'me' ? '/users/me/activities' : `/users/${userId}/activities`;
  const res = await apiClient.get<ApiResponse<{ items: ActivityItem[]; total: number }>>(url, {
    params: { page, page_size: pageSize },
  });
  return res.data.data;
}
