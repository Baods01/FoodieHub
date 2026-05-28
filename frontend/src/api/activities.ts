// 用户动态（活动）接口
// TODO: 当前后端无独立的活动 HTTP 端点
// 活动数据通过信号机制自动写入，未来可通过以下方式获取：
// - 用户主页：GET /users/me/timeline（待开发）
// - 特定类型：GET /activities?type=comment&page=1（待开发）

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

import apiClient from './client';
import type { ApiResponse } from '../types/common';

/** 获取用户动态列表 */
export async function fetchActivities(userId: number | 'me', page = 1, pageSize = 20): Promise<{ items: ActivityItem[]; total: number }> {
  const url = userId === 'me' ? '/users/me/activities' : `/users/${userId}/activities`;
  try {
    const res = await apiClient.get<ApiResponse<{ items: ActivityItem[]; total: number }>>(url, {
      params: { page, page_size: pageSize },
    });
    return res.data.data;
  } catch {
    return { items: [], total: 0 };
  }
}
