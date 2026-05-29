import apiClient from './client';
import type { ApiResponse } from '../types/common';

// ============ 类型定义 ============

export interface ShopCardData {
  id: number;
  name: string;
  average_rating: number;
  view_count: number;
  favorite_count: number;
  comment_count: number;
  cover_image: string | null;
  dict_data: { id: number; name: string }[];
  is_favorited: boolean;
  created_at: string;
}

export interface ShopDetail extends ShopCardData {
  rating_distribution: { star_1: number; star_2: number; star_3: number; star_4: number; star_5: number; total: number };
  aliases: string[] | null;
  merged_into_id: number | null;
  is_banned: boolean;
  menu_items: MenuItem[];
  images: { id: number; url: string }[];
  user_rating: { score: number } | null;
  updated_at: string;
}

export interface MenuItem {
  id: number;
  shop_id: number;
  name: string;
  price: number | null;
  description: string | null;
  created_at: string;
}

export interface ShopFilter {
  keyword?: string;
  category_ids?: number[];
  district_ids?: number[];
  min_rating?: number;
  sort_by?: string;
  sort_order?: string;
  page: number;
  page_size: number;
}

export interface CreateShopData {
  name: string;
  dict_data_ids: number[];
  menu_items?: { name: string; price?: number; description?: string }[];
}

export interface UpdateShopData {
  name?: string;
  dict_data_ids?: number[];
  is_active?: boolean;
}

export interface DictItem {
  id: number;
  dict_type_id: number;
  name: string;
}

export interface DictType {
  id: number;
  name: string;
  target_table: string;
}

// ============ 店铺接口 ============

export async function fetchShops(filter: ShopFilter): Promise<{ items: ShopCardData[]; total: number }> {
  const params: Record<string, any> = {
    keyword: filter.keyword || undefined,
    category_ids: filter.category_ids?.length ? filter.category_ids.join(',') : undefined,
    district_ids: filter.district_ids?.length ? filter.district_ids.join(',') : undefined,
    min_rating: filter.min_rating,
    sort_by: filter.sort_by || 'favorite_count',
    sort_order: filter.sort_order || 'desc',
    page: filter.page,
    page_size: filter.page_size || 20,
  };
  const res = await apiClient.get<ApiResponse<{ items: ShopCardData[]; total: number }>>('/shops', { params });
  return res.data.data;
}

export async function fetchShopDetail(shopId: number): Promise<ShopDetail> {
  const res = await apiClient.get<ApiResponse<ShopDetail>>(`/shops/${shopId}`);
  return res.data.data;
}

export async function createShopApi(data: CreateShopData): Promise<ShopDetail> {
  const res = await apiClient.post<ApiResponse<ShopDetail>>('/shops', data);
  return res.data.data;
}

export async function updateShopApi(shopId: number, data: UpdateShopData): Promise<ShopDetail> {
  const res = await apiClient.put<ApiResponse<ShopDetail>>(`/shops/${shopId}`, data);
  return res.data.data;
}

export async function deleteShopApi(shopId: number): Promise<void> {
  await apiClient.delete(`/shops/${shopId}`);
}

// ============ 评分接口 ============

export async function submitRating(shopId: number, score: number): Promise<{ average_rating: number; rating_distribution: any }> {
  const res = await apiClient.post<ApiResponse<{ average_rating: number; rating_distribution: any }>>(`/shops/${shopId}/rating`, { score });
  return res.data.data;
}

// ============ 菜单接口 ============

export async function fetchMenu(shopId: number): Promise<MenuItem[]> {
  const res = await apiClient.get<ApiResponse<MenuItem[]>>(`/shops/${shopId}/menu`);
  return res.data.data;
}

export async function addMenuItem(shopId: number, name: string, price?: number, description?: string): Promise<MenuItem> {
  const res = await apiClient.post<ApiResponse<MenuItem>>(`/shops/${shopId}/menu`, null, {
    params: { name, price, description },
  });
  return res.data.data;
}

// ============ 字典接口 ============

export async function fetchDictTypes(): Promise<{ id: number; name: string }[]> {
  const res = await apiClient.get('/dict/types');
  return (res.data as any).data;
}


