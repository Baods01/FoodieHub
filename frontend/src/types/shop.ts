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

/** 店铺详情数据（详情页用，暂留占位） */
export interface ShopDetail extends ShopCardData {
  description: string;
  menu: MenuItem[];
  environmentImages: string[];
  ratingDistribution: Record<1 | 2 | 3 | 4 | 5, number>;
}

export interface MenuItem {
  id: number;
  name: string;
  price: number;
  description: string;
  image: string | null;
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
