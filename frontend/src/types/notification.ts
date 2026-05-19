export type NotifType = 'reply' | 'like' | 'announcement';

export interface NotificationItem {
  id: number;
  type: NotifType;
  /** 展示用描述文字，如「陈同学回复了你的评论」 */
  description: string;
  /** 关联店铺 ID（用于跳转） */
  shopId: number;
  /** 是否已读 */
  isRead: boolean;
  /** ISO 时间 */
  createdAt: string;
  /** 仅公告类使用：标题 */
  title?: string;
  /** 仅公告类使用：完整正文 */
  fullContent?: string;
}
