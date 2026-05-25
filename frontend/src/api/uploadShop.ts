// 对接后端时取消注释:
// import apiClient from './client';
// import type { ApiResponse } from '../types/common';

export interface CreateShopRequest {
  name: string;
  dict_data_codes: string[];   // 品类 code + 区域 code
  dining_methods: string[];    // 就餐方式 codes
}

export interface CreateShopResponse {
  id: number;
  name: string;
}

/** 创建店铺 */
export async function createShop(data: CreateShopRequest): Promise<CreateShopResponse> {
  // const res = await apiClient.post<ApiResponse<CreateShopResponse>>('/shops', data);
  // return res.data.data;
  return mockCreateShop(data);
}

// ============ Mock ============

let nextId = 100;

const delay = (ms = 600) => new Promise((r) => setTimeout(r, ms + Math.random() * 400));

async function mockCreateShop(data: CreateShopRequest): Promise<CreateShopResponse> {
  await delay();
  const id = nextId++;
  return { id, name: data.name };
}
