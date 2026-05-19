import type { NotificationItem } from '../types/notification';

// 对接后端时取消注释:
// import apiClient from './client';
// import type { ApiResponse } from '../types/common';

/** 获取全部消息 */
export async function fetchNotifications(): Promise<NotificationItem[]> {
  // const { data } = await apiClient.get<ApiResponse<NotificationItem[]>>('/notifications');
  // return data.data;
  return mockFetch();
}

/** 标记单条为已读 */
export async function markAsRead(id: number): Promise<boolean> {
  // await apiClient.post(`/notifications/${id}/read`);
  return mockMarkRead(id);
}

// ============ Mock ============

const delay = (ms = 350) => new Promise((r) => setTimeout(r, ms + Math.random() * 300));

let mockData: NotificationItem[] = [
  // ——— 回复我的 ———
  { id: 1, type: 'reply', description: '陈同学回复了你的评论', shopId: 1, isRead: false, createdAt: new Date(Date.now() - 1 * 3600000).toISOString() },
  { id: 2, type: 'reply', description: '李学长回复了你的评论', shopId: 17, isRead: false, createdAt: new Date(Date.now() - 5 * 3600000).toISOString() },
  { id: 3, type: 'reply', description: '糖水老板回复了你的评论', shopId: 1, isRead: true, createdAt: new Date(Date.now() - 3 * 86400000).toISOString() },
  { id: 4, type: 'reply', description: '王老师回复了你的评论', shopId: 5, isRead: true, createdAt: new Date(Date.now() - 7 * 86400000).toISOString() },
  // ——— 收到的赞 ———
  { id: 5, type: 'like', description: '陈同学赞了你的评论', shopId: 1, isRead: false, createdAt: new Date(Date.now() - 2 * 3600000).toISOString() },
  { id: 6, type: 'like', description: '李学长赞了你的评论', shopId: 1, isRead: false, createdAt: new Date(Date.now() - 1 * 86400000).toISOString() },
  { id: 7, type: 'like', description: '美食家赞了你的评论', shopId: 17, isRead: true, createdAt: new Date(Date.now() - 10 * 86400000).toISOString() },
  // ——— 系统通知 ———
  { id: 8, type: 'announcement', description: '食探社正式上线啦！🎉', shopId: 0, isRead: false, createdAt: new Date(Date.now() - 2 * 86400000).toISOString(), title: '食探社正式上线', fullContent: '欢迎来到食探社——华农校园美食社区！\n\n在这里，你可以发现身边的宝藏美食店铺，分享真实的美食体验，与同学们一起共建校园美食地图。\n\n目前平台已收录校内及周边 20+ 家店铺，欢迎各位同学踊跃上传和点评！\n\n——食探社运营团队' },
  { id: 9, type: 'announcement', description: '社区公约 v1.0 发布', shopId: 0, isRead: true, createdAt: new Date(Date.now() - 14 * 86400000).toISOString(), title: '社区公约 v1.0', fullContent: '为维护良好的社区氛围，请所有用户遵守以下公约：\n\n1. 请勿发布虚假店铺信息\n2. 点评内容应真实、客观\n3. 禁止恶意刷评、刷分\n4. 尊重他人，友善交流\n\n违反公约的内容将被管理员处理。' },
];

async function mockFetch(): Promise<NotificationItem[]> {
  await delay();
  return [...mockData].sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());
}

async function mockMarkRead(id: number): Promise<boolean> {
  await delay(150);
  mockData = mockData.map((n) => (n.id === id ? { ...n, isRead: true } : n));
  return true;
}
