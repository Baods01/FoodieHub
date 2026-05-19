import type { FavoriteItem } from '../types/favorite';

// 对接后端时取消注释:
// import apiClient from './client';
// import type { ApiResponse } from '../types/common';

/** 获取收藏列表 */
export async function fetchFavorites(): Promise<FavoriteItem[]> {
  // const { data } = await apiClient.get<ApiResponse<FavoriteItem[]>>('/favorites');
  // return data.data;
  return mockFetchFavorites();
}

/** 取消收藏，返回是否成功 */
export async function removeFavorite(shopId: number): Promise<boolean> {
  // await apiClient.post(`/shops/${shopId}/favorite`);
  // return true;
  return mockRemoveFavorite(shopId);
}

// ============ Mock ============

const delay = (ms = 400) => new Promise((r) => setTimeout(r, ms + Math.random() * 400));

/** 模拟收藏数据库 */
let mockFavorites: FavoriteItem[] = [
  {
    id: 1, name: '陈记糖水铺', category: '糖水', area: '华农西门',
    rating: 4.5, reviewCount: 42, favoriteCount: 320, viewCount: 2500,
    coverImage: 'https://picsum.photos/seed/shop1/400/225',
    tags: ['招牌芋圆'],
    favoritedAt: new Date(Date.now() - 2 * 86400000).toISOString(),
  },
  {
    id: 2, name: '重庆老火锅', category: '火锅', area: '华农南门',
    rating: 4.8, reviewCount: 65, favoriteCount: 480, viewCount: 4200,
    coverImage: 'https://picsum.photos/seed/shop2/400/225',
    tags: ['辣', '排队王'],
    favoritedAt: new Date(Date.now() - 5 * 86400000).toISOString(),
  },
  {
    id: 5, name: '东北烤肉坊', category: '烧烤', area: '华农西门',
    rating: 4.6, reviewCount: 55, favoriteCount: 410, viewCount: 3800,
    coverImage: 'https://picsum.photos/seed/shop5/400/225',
    tags: ['性价比高'],
    favoritedAt: new Date(Date.now() - 8 * 86400000).toISOString(),
  },
  {
    id: 17, name: '潮汕牛肉火锅', category: '火锅', area: '华农南门',
    rating: 4.9, reviewCount: 78, favoriteCount: 490, viewCount: 4800,
    coverImage: null,
    tags: ['牛肉丸', '沙茶酱'],
    favoritedAt: new Date(Date.now() - 12 * 86400000).toISOString(),
  },
];

async function mockFetchFavorites(): Promise<FavoriteItem[]> {
  await delay();
  // 按收藏时间倒序
  return [...mockFavorites].sort(
    (a, b) => new Date(b.favoritedAt).getTime() - new Date(a.favoritedAt).getTime()
  );
}

async function mockRemoveFavorite(shopId: number): Promise<boolean> {
  await delay(300);
  mockFavorites = mockFavorites.filter((f) => f.id !== shopId);
  return true;
}

/** 供排序使用的纯客户端排序（不请求后端） */
export function sortFavorites(items: FavoriteItem[], sort: string): FavoriteItem[] {
  const sorted = [...items];
  switch (sort) {
    case 'rating':
      return sorted.sort((a, b) => b.rating - a.rating);
    case 'name':
      return sorted.sort((a, b) => a.name.localeCompare(b.name, 'zh-CN'));
    default: // 'time'
      return sorted.sort((a, b) => new Date(b.favoritedAt).getTime() - new Date(a.favoritedAt).getTime());
  }
}
