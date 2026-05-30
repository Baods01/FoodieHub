import apiClient from './client';
import type { ApiResponse } from '../types/common';

export interface FeedbackRequest {
  type: 'complaint' | 'edit_request';
  target_type: string;
  target_id: number;
  reason_id: number;
  description?: string;
}

export interface FeedbackResponse {
  id: number;
  status: string;
}

export async function submitFeedback(data: FeedbackRequest): Promise<FeedbackResponse> {
  const res = await apiClient.post<ApiResponse<FeedbackResponse>>('/complaints', data);
  return res.data.data;
}
