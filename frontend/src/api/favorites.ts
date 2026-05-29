import apiClient from './client';
import type { ApiResponse } from '../types/common';

export interface FavoriteItem {
  id: number;
  user_id: number;
  shop_id: number;
  shop_name: string | null;
  shop_cover: string | null;
  created_at: string;
}

export interface ToggleResult {
  is_favorited: boolean;
  favorite_count: number;
}

export async function toggleFavorite(shopId: number): Promise<ToggleResult> {
  const res = await apiClient.post<ApiResponse<ToggleResult>>('/favorites/toggle', null, { params: { shop_id: shopId } });
  return res.data.data;
}

export async function fetchFavorites(page = 1, pageSize = 20): Promise<{ items: FavoriteItem[]; total: number }> {
  const res = await apiClient.get<ApiResponse<{ items: FavoriteItem[]; total: number }>>('/favorites/user', {
    params: { page, page_size: pageSize },
  });
  return res.data.data;
}
