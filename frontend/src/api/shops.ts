import type { ShopCardData, ShopFilter } from '../types/shop';
import type { PaginatedResult } from '../types/common';

// ===== 接口签名（预留给后端对接） =====
// 对接后取消注释以下 import 并删除 mock 分支:
// import apiClient from './client';
// import type { ApiResponse } from '../types/common';

export async function fetchShops(filter: ShopFilter): Promise<PaginatedResult<ShopCardData>> {
  // const params = { keyword: filter.keyword, sort: filter.sort, category: filter.category, area: filter.area, page: filter.page, page_size: 12 };
  // const { data } = await apiClient.get<ApiResponse<PaginatedResult<ShopCardData>>>('/shops', { params });
  // return data.data;
  return mockFetchShops(filter);
}

export async function fetchCategories(): Promise<string[]> {
  // const { data } = await apiClient.get<ApiResponse<string[]>>('/dictionaries/categories');
  // return data.data;
  return mockCategories();
}

export async function fetchAreas(): Promise<string[]> {
  // const { data } = await apiClient.get<ApiResponse<string[]>>('/dictionaries/areas');
  // return data.data;
  return mockAreas();
}

export async function fetchAnnouncement(): Promise<{ title: string; content: string } | null> {
  // const { data } = await apiClient.get<ApiResponse<{ title: string; content: string } | null>>('/announcements/active');
  // return data.data;
  return mockAnnouncement();
}

// ===== Mock 数据 =====

const delay = () => new Promise((r) => setTimeout(r, 200 + Math.random() * 600));

const mockShopData: ShopCardData[] = [
  { id: 1, name: '陈记糖水铺', category: '糖水', area: '华农西门', rating: 4.5, reviewCount: 42, favoriteCount: 320, viewCount: 2500, coverImage: 'https://picsum.photos/seed/shop1/400/225', tags: ['招牌芋圆'] },
  { id: 2, name: '重庆老火锅', category: '火锅', area: '华农南门', rating: 4.8, reviewCount: 65, favoriteCount: 480, viewCount: 4200, coverImage: 'https://picsum.photos/seed/shop2/400/225', tags: ['辣', '排队王'] },
  { id: 3, name: '潮味粉面馆', category: '粉面', area: '华农北门', rating: 4.2, reviewCount: 28, favoriteCount: 180, viewCount: 1500, coverImage: 'https://picsum.photos/seed/shop3/400/225', tags: ['牛肉丸'] },
  { id: 4, name: '麦香基快餐', category: '快餐', area: '校内', rating: 3.8, reviewCount: 15, favoriteCount: 95, viewCount: 800, coverImage: 'https://picsum.photos/seed/shop4/400/225', tags: [] },
  { id: 5, name: '东北烤肉坊', category: '烧烤', area: '华农西门', rating: 4.6, reviewCount: 55, favoriteCount: 410, viewCount: 3800, coverImage: 'https://picsum.photos/seed/shop5/400/225', tags: ['性价比高'] },
  { id: 6, name: '樱花寿司屋', category: '日料', area: '华农南门', rating: 4.3, reviewCount: 38, favoriteCount: 260, viewCount: 2100, coverImage: null, tags: ['三文鱼'] },
  { id: 7, name: '街角小吃王', category: '小吃', area: '华农北门', rating: 4.0, reviewCount: 22, favoriteCount: 150, viewCount: 1200, coverImage: null, tags: [] },
  { id: 8, name: '一点点奶茶', category: '饮品', area: '华农西门', rating: 4.1, reviewCount: 80, favoriteCount: 500, viewCount: 5000, coverImage: null, tags: ['波霸'] },
  { id: 9, name: '其他美食汇', category: '其他', area: '其他', rating: 3.5, reviewCount: 8, favoriteCount: 45, viewCount: 350, coverImage: null, tags: [] },
  { id: 10, name: '老王快餐', category: '快餐', area: '华农北门', rating: 2.5, reviewCount: 5, favoriteCount: 25, viewCount: 150, coverImage: null, tags: [] },
  { id: 11, name: '深夜烧烤摊', category: '烧烤', area: '华农西门', rating: 4.4, reviewCount: 48, favoriteCount: 350, viewCount: 2900, coverImage: null, tags: ['夜宵'] },
  { id: 12, name: '甜蜜蜜糖水', category: '糖水', area: '华农南门', rating: 4.7, reviewCount: 58, favoriteCount: 430, viewCount: 3600, coverImage: null, tags: ['杨枝甘露'] },
  { id: 13, name: '兰州拉面', category: '粉面', area: '华农西门', rating: 4.0, reviewCount: 35, favoriteCount: 220, viewCount: 1800, coverImage: null, tags: [] },
  { id: 14, name: '寿司大满贯', category: '日料', area: '校内', rating: 4.2, reviewCount: 30, favoriteCount: 200, viewCount: 1600, coverImage: null, tags: ['自助'] },
  { id: 15, name: '水果茶先生', category: '饮品', area: '华农南门', rating: 4.3, reviewCount: 72, favoriteCount: 460, viewCount: 4500, coverImage: null, tags: ['鲜果'] },
  { id: 16, name: '卤味研究所', category: '小吃', area: '华农北门', rating: 3.0, reviewCount: 12, favoriteCount: 60, viewCount: 500, coverImage: null, tags: [] },
  { id: 17, name: '潮汕牛肉火锅', category: '火锅', area: '华农南门', rating: 4.9, reviewCount: 78, favoriteCount: 490, viewCount: 4800, coverImage: null, tags: ['牛肉丸', '沙茶酱'] },
  { id: 18, name: '川味麻辣烫', category: '快餐', area: '华农西门', rating: 4.1, reviewCount: 40, favoriteCount: 280, viewCount: 2200, coverImage: null, tags: ['辣'] },
  { id: 19, name: '日式拉面屋', category: '日料', area: '华农北门', rating: 4.5, reviewCount: 50, favoriteCount: 340, viewCount: 2800, coverImage: null, tags: ['豚骨'] },
  { id: 20, name: '烤鱼专家', category: '其他', area: '华农西门', rating: 4.6, reviewCount: 45, favoriteCount: 380, viewCount: 3100, coverImage: null, tags: ['清江鱼'] },
];

const categories = ['糖水', '火锅', '粉面', '快餐', '烧烤', '日料', '小吃', '饮品', '其他'];
const areas = ['华农西门', '华农南门', '华农北门', '校内', '其他'];

function mockCategories(): string[] {
  return categories;
}

function mockAreas(): string[] {
  return areas;
}

function mockAnnouncement(): { title: string; content: string } | null {
  return {
    title: '🎉 食探社正式上线！',
    content: '欢迎来到华农校园美食社区，分享你身边的宝藏美食店铺。',
  };
}

function mockFetchShops(filter: ShopFilter): Promise<PaginatedResult<ShopCardData>> {
  const pageSize = 12;

  let filtered = [...mockShopData];

  if (filter.keyword) {
    const kw = filter.keyword.toLowerCase();
    filtered = filtered.filter((s) => s.name.toLowerCase().includes(kw));
  }

  if (filter.category) {
    filtered = filtered.filter((s) => s.category === filter.category);
  }

  if (filter.area) {
    filtered = filtered.filter((s) => s.area === filter.area);
  }

  switch (filter.sort) {
    case 'newest':
      filtered.sort((a, b) => b.id - a.id);
      break;
    case 'favorites':
      filtered.sort((a, b) => b.favoriteCount - a.favoriteCount);
      break;
    case 'views':
      filtered.sort((a, b) => b.viewCount - a.viewCount);
      break;
    case 'rating':
      filtered.sort((a, b) => b.rating - a.rating || b.reviewCount - a.reviewCount);
      break;
    case 'reviews':
      filtered.sort((a, b) => b.reviewCount - a.reviewCount);
      break;
  }

  const total = filtered.length;
  const start = (filter.page - 1) * pageSize;
  const data = filtered.slice(start, start + pageSize);

  return delay().then(() => ({
    data,
    total,
    page: filter.page,
    pageSize,
    hasMore: start + pageSize < total,
  }));
}
