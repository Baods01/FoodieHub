import type { HistoryItem } from '../types/history';

// 对接后端时取消注释:
// import apiClient from './client';
// import type { ApiResponse } from '../types/common';

/** 获取浏览历史（不重复店铺） */
export async function fetchHistory(): Promise<HistoryItem[]> {
  // const { data } = await apiClient.get<ApiResponse<HistoryItem[]>>('/history');
  // return data.data;
  return mockFetchHistory();
}

/** 移除单条浏览记录 */
export async function removeHistory(shopId: number): Promise<boolean> {
  // await apiClient.delete(`/history/${shopId}`);
  return mockRemoveHistory(shopId);
}

/** 清空全部浏览记录 */
export async function clearHistory(): Promise<boolean> {
  // await apiClient.delete('/history');
  return mockClearHistory();
}

// ============ Mock ============

const delay = (ms = 400) => new Promise((r) => setTimeout(r, ms + Math.random() * 400));

let mockData: HistoryItem[] = [
  {
    id: 1, name: '陈记糖水铺', category: '糖水', area: '华农西门',
    rating: 4.5, reviewCount: 42, favoriteCount: 320, viewCount: 2500,
    coverImage: 'https://picsum.photos/seed/shop1/400/225',
    tags: ['招牌芋圆'],
    viewedAt: new Date(Date.now() - 1 * 3600000).toISOString(),
  },
  {
    id: 17, name: '潮汕牛肉火锅', category: '火锅', area: '华农南门',
    rating: 4.9, reviewCount: 78, favoriteCount: 490, viewCount: 4800,
    coverImage: null,
    tags: ['牛肉丸', '沙茶酱'],
    viewedAt: new Date(Date.now() - 5 * 3600000).toISOString(),
  },
  {
    id: 2, name: '重庆老火锅', category: '火锅', area: '华农南门',
    rating: 4.8, reviewCount: 65, favoriteCount: 480, viewCount: 4200,
    coverImage: 'https://picsum.photos/seed/shop2/400/225',
    tags: ['辣', '排队王'],
    viewedAt: new Date(Date.now() - 24 * 3600000).toISOString(),
  },
  {
    id: 5, name: '东北烤肉坊', category: '烧烤', area: '华农西门',
    rating: 4.6, reviewCount: 55, favoriteCount: 410, viewCount: 3800,
    coverImage: 'https://picsum.photos/seed/shop5/400/225',
    tags: ['性价比高'],
    viewedAt: new Date(Date.now() - 3 * 86400000).toISOString(),
  },
  {
    id: 8, name: '一点点奶茶', category: '饮品', area: '华农西门',
    rating: 4.1, reviewCount: 80, favoriteCount: 500, viewCount: 5000,
    coverImage: null,
    tags: ['波霸'],
    viewedAt: new Date(Date.now() - 7 * 86400000).toISOString(),
  },
];

async function mockFetchHistory(): Promise<HistoryItem[]> {
  await delay();
  return [...mockData].sort(
    (a, b) => new Date(b.viewedAt).getTime() - new Date(a.viewedAt).getTime()
  );
}

async function mockRemoveHistory(shopId: number): Promise<boolean> {
  await delay(300);
  mockData = mockData.filter((h) => h.id !== shopId);
  return true;
}

async function mockClearHistory(): Promise<boolean> {
  await delay(300);
  mockData = [];
  return true;
}
