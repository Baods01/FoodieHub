import apiClient from './client';
import type { ApiResponse } from '../types/common';

export interface NotificationItem {
  id: number;
  type: string;
  title: string | null;
  content: string;
  is_read: boolean;
  created_at: string;
  related_entity_type: string | null;
  related_entity_id: number | null;
  sender: { id: number; username: string; avatar: string | null } | null;
}

export interface NotificationListResult {
  items: NotificationItem[];
  total: number;
  page: number;
  page_size: number;
  unread_count: number;
}

/** 获取消息列表 */
export async function fetchNotifications(page = 1, pageSize = 20, unreadOnly = false): Promise<NotificationListResult> {
  const res = await apiClient.get<ApiResponse<NotificationListResult>>('/messages', {
    params: { page, page_size: pageSize, unread_only: unreadOnly },
  });
  return res.data.data;
}

/** 获取未读数 */
export async function fetchUnreadCount(): Promise<number> {
  const res = await apiClient.get<ApiResponse<{ unread_count: number }>>('/messages/unread-count');
  return res.data.data.unread_count;
}

/** 标记已读 */
export async function markAsRead(messageIds: number[]): Promise<number> {
  const res = await apiClient.post<ApiResponse<{ marked_count: number }>>('/messages/mark-read', { message_ids: messageIds });
  return res.data.data.marked_count;
}

/** 全部已读 */
export async function markAllAsRead(): Promise<number> {
  const res = await apiClient.post<ApiResponse<{ marked_count: number }>>('/messages/mark-all-read');
  return res.data.data.marked_count;
}

/** 清空消息 */
export async function clearAllNotifications(): Promise<number> {
  const res = await apiClient.delete<ApiResponse<{ deleted_count: number }>>('/messages/clear-all');
  return res.data.data.deleted_count;
}
