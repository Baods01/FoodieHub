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
