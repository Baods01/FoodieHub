/** 店铺卡片数据（主页列表展示用） */
export interface ShopCardData {
  id: number;
  name: string;
  category: string;
  area: string;
  rating: number;
  reviewCount: number;
  favoriteCount: number;
  viewCount: number;
  coverImage: string | null;
  tags: string[];
}

/** 店铺详情数据 */
export interface ShopDetail extends ShopCardData {
  description: string;
  menu: MenuItem[];
  albumImages: string[];
  ratingDistribution: Record<1 | 2 | 3 | 4 | 5, number>;
  totalRatings: number;
  userRating: number | null;
  isFavorited: boolean;
  diningMethods?: string[]; // 显示名称，如 ['堂食', '自取', '外卖']
}

export interface MenuItem {
  id: number;
  name: string;
  price: number;
  description: string;
  image: string | null;
}

/** 评分提交请求 */
export interface RatingSubmit {
  shopId: number;
  rating: number;
}

/** 排序选项 */
export type SortOption = 'newest' | 'favorites' | 'views' | 'rating' | 'reviews';

/** 筛选条件 */
export interface ShopFilter {
  keyword: string;
  sort: SortOption;
  category: string;
  area: string;
  page: number;
}
