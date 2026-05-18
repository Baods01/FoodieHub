import type { Activity } from '../types/activity';

// 对接后端时取消注释:
// import apiClient from './client';
// import type { ApiResponse } from '../types/common';

/** 获取用户动态列表 */
export async function fetchActivities(userId: number): Promise<Activity[]> {
  // const { data } = await apiClient.get<ApiResponse<Activity[]>>(`/users/${userId}/activities`);
  // return data.data;
  return mockFetchActivities(userId);
}

// ============ Mock ============

const delay = () => new Promise((r) => setTimeout(r, 300 + Math.random() * 300));

function mockFetchActivities(_userId: number): Promise<Activity[]> {
  const now = Date.now();

  const mockData: Activity[] = [
    {
      id: 1,
      type: 'rating',
      content: `评分了「陈记糖水铺」`,
      shopName: '陈记糖水铺',
      shopId: 1,
      createdAt: new Date(now - 2 * 3600000).toISOString(),
      extra: { score: 5 },
    },
    {
      id: 2,
      type: 'comment',
      content: `评论了「陈记糖水铺」`,
      shopName: '陈记糖水铺',
      shopId: 1,
      createdAt: new Date(now - 24 * 3600000).toISOString(),
    },
    {
      id: 3,
      type: 'favorite',
      content: `收藏了「潮汕牛肉火锅」`,
      shopName: '潮汕牛肉火锅',
      shopId: 17,
      createdAt: new Date(now - 3 * 24 * 3600000).toISOString(),
    },
    {
      id: 4,
      type: 'add_shop',
      content: `上传了新店铺「东北烤肉坊」`,
      shopName: '东北烤肉坊',
      shopId: 5,
      createdAt: new Date(now - 5 * 24 * 3600000).toISOString(),
    },
    {
      id: 5,
      type: 'question',
      content: `提问了「陈记糖水铺」：这里有没有空调？`,
      shopName: '陈记糖水铺',
      shopId: 1,
      createdAt: new Date(now - 7 * 24 * 3600000).toISOString(),
    },
    {
      id: 6,
      type: 'rating',
      content: `评分了「潮汕牛肉火锅」`,
      shopName: '潮汕牛肉火锅',
      shopId: 17,
      createdAt: new Date(now - 10 * 24 * 3600000).toISOString(),
      extra: { score: 5 },
    },
  ];

  return delay().then(() => mockData);
}
