/** 字典数据项（后端 DictDataSimpleResponse） */
export interface DictDataItem {
  id: number;
  name: string;
  dict_type_name: string;
  extra?: Record<string, any>;
}

/** 店铺卡片数据（主页列表展示用）— 对齐后端 ShopResponse */
export interface ShopCardData {
  id: number;
  name: string;
  average_rating: number;
  view_count: number;
  favorite_count: number;
  comment_count: number;
  cover_image: string | null;
  dict_data: DictDataItem[];
  is_favorited: boolean;
  created_at: string;
}

/** 评分分布 */
export interface RatingDistribution {
  star_1: number;
  star_2: number;
  star_3: number;
  star_4: number;
  star_5: number;
  total: number;
}

/** 菜单项 */
export interface MenuItem {
  id: number;
  name: string;
  price: number;
  description?: string;
  image?: string | null;
}

/** 图片项 */
export interface ImageItem {
  id: number;
  url: string;
}

/** 店铺详情数据 — 对齐后端 ShopResponse */
export interface ShopDetail {
  description?: string;
  id: number;
  name: string;
  average_rating: number;
  view_count: number;
  favorite_count: number;
  comment_count: number;
  cover_image: string | null;
  dict_data: DictDataItem[];
  is_favorited: boolean;
  created_at: string;
  updated_at: string;
  is_banned: boolean;
  rating_distribution: RatingDistribution;
  menu_items: MenuItem[];
  images: ImageItem[];
  user_rating: { score: number } | null;
}

/** 排序选项（与后端 sort_by 对齐） */
export type SortOption = 'favorite_count' | 'average_rating' | 'view_count' | 'created_at';

/** 筛选参数 — 对齐后端搜索接口 */
export interface ShopFilter {
  keyword?: string;
  category_ids?: number[];
  district_ids?: number[];
  min_rating?: number;
  sort_by?: 'favorite_count' | 'average_rating' | 'view_count' | 'created_at';
  sort_order?: 'asc' | 'desc';
  page: number;
  page_size?: number;
}

/** 按 dict_type_name 分组提取标签名 */
export function getDictNamesByType(dictData: DictDataItem[], typeName: string): string[] {
  return dictData.filter(d => d.dict_type_name === typeName).map(d => d.name);
}

/** 取品类中文名（首项） */
export function getCategoryName(dictData: DictDataItem[]): string {
  return getDictNamesByType(dictData, '品类')[0] ?? '';
}

/** 取区域中文名（首项） */
export function getAreaName(dictData: DictDataItem[]): string {
  return getDictNamesByType(dictData, '区域')[0] ?? '';
}

/** 取就餐方式列表 */
export function getDiningMethods(dictData: DictDataItem[]): string[] {
  return getDictNamesByType(dictData, '就餐方式');
}
