import apiClient from './client';
import type { ApiResponse } from '../types/common';

export interface CreateShopRequest {
  name: string;
  dict_data_ids: number[];
  menu_items?: { name: string; price?: number; description?: string }[];
}

export interface CreateShopResponse {
  id: number;
  name: string;
}

export async function createShop(data: CreateShopRequest): Promise<CreateShopResponse> {
  const res = await apiClient.post<ApiResponse<CreateShopResponse>>('/shops', data);
  return res.data.data;
}
