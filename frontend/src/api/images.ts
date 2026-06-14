import apiClient from './client';
import type { ApiResponse } from '../types/common';

/** 删除图片 */
export async function deleteImage(imageId: number): Promise<void> {
  await apiClient.delete<ApiResponse<null>>(`/images/${imageId}`);
}