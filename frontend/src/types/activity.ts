export type ActivityType = 'rating' | 'comment' | 'favorite' | 'add_shop' | 'question';

export interface Activity {
  id: number;
  type: ActivityType;
  content: string;
  shopName: string;
  shopId: number;
  createdAt: string;
  extra?: {
    score?: number;
  };
}
