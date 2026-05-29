export type ActivityType = 'rating' | 'comment' | 'favorite' | 'add_shop' | 'question';

export interface Activity {
  id: number;
  user_id: number;
  type: ActivityType;
  target_id: number;
  target_type: string;
  content: string | null;
  shop_id: number | null;
  shop_name: string | null;
  created_at: string;
}

/** 根据 type 生成动态展示文字 */
export function getActivityText(type: ActivityType): string {
  const map: Record<ActivityType, string> = {
    rating: '进行了评分',
    comment: '发表了评论',
    favorite: '收藏了店铺',
    add_shop: '分享了新店铺',
    question: '提出了问题',
  };
  return map[type] ?? '产生了新动态';
}
