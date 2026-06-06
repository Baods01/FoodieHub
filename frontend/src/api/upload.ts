import apiClient from './client';
import type { ApiResponse } from '../types/common';

/** 上传图片 */
export async function uploadImage(
  file: File,
  entityType: string,
  entityId: number,
): Promise<{ id: number; url: string }> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('entity_type', entityType);
  formData.append('entity_id', String(entityId));

  const res = await apiClient.post<ApiResponse<{ id: number; url: string }>>('/images/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return res.data.data;
}

/** 获取首页轮播图列表（按实体类型聚合） */
export async function fetchBannerImages(): Promise<{ id: number; url: string }[]> {
  const res = await apiClient.get<ApiResponse<{ items: { id: number; url: string }[] }>>('/images', {
    params: { entity_type: 'shop', page: 1, page_size: 50, order: 'random' },
  });
  return res.data.data.items ?? [];
}
