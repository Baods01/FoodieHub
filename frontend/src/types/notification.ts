/** 通知类型标签（前端展示用） */
export type NotifType = 'reply_comment' | 'like_comment' | 'announcement';

/** 消息通知 — 对齐后端 MessageResponse */
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

/** 通知类型 → 中文标签 */
export function getNotifTypeLabel(type: string): string {
  const map: Record<string, string> = {
    reply_comment: '回复我的',
    like_comment: '收到的赞',
    announcement: '系统通知',
  };
  return map[type] ?? type;
}

/** 关联实体 → 前端路由（用于点击消息跳转） */
export function getNotifRoute(entityType: string | null, entityId: number | null): string | null {
  if (!entityType || !entityId) return null;
  if (entityType === 'shop') return `/shop/${entityId}`;
  return null;
}
