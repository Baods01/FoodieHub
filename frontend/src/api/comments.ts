import apiClient from './client';
import type { ApiResponse } from '../types/common';

// ============ 类型定义 ============

export interface CommentData {
  id: number;
  shop_id: number;
  user: { id: number; username: string; avatar: string | null } | null;
  content: string;
  like_count: number;
  reply_count: number;
  has_liked: boolean;
  created_at: string;
}

export interface ReplyData {
  id: number;
  comment_id: number;
  user: { id: number; username: string; avatar: string | null } | null;
  content: string;
  reply_to_user: { id: number; username: string } | null;
  like_count: number;
  has_liked: boolean;
  created_at: string;
}

export interface QuestionData {
  id: number;
  shop_id: number;
  user: { id: number; username: string; avatar: string | null } | null;
  title: string;
  content: string | null;
  like_count: number;
  created_at: string;
}

export interface AnswerData {
  id: number;
  question_id: number;
  user: { id: number; username: string; avatar: string | null } | null;
  content: string;
  reply_to_user: { id: number; username: string } | null;
  like_count: number;
  has_liked: boolean;
  created_at: string;
}

// ============ 评论接口 ============

export async function fetchComments(shopId: number, page = 1, pageSize = 20): Promise<{ items: CommentData[]; total: number }> {
  const res = await apiClient.get<ApiResponse<{ items: CommentData[]; total: number }>>(`/shops/${shopId}/comments`, {
    params: { page, page_size: pageSize },
  });
  return res.data.data;
}

export async function postComment(shopId: number, content: string): Promise<any> {
  const res = await apiClient.post<ApiResponse<any>>(`/shops/${shopId}/comments`, { content });
  return res.data.data;
}

export async function updateComment(commentId: number, content: string): Promise<any> {
  const res = await apiClient.put<ApiResponse<any>>(`/comments/${commentId}`, { content });
  return res.data.data;
}

export async function deleteComment(commentId: number): Promise<void> {
  await apiClient.delete(`/comments/${commentId}`);
}

// ============ 回复接口 ============

export async function fetchReplies(commentId: number): Promise<ReplyData[]> {
  const res = await apiClient.get<ApiResponse<ReplyData[]>>(`/comments/${commentId}/replies`);
  return res.data.data;
}

export async function postReply(commentId: number, content: string, replyToUserId?: number): Promise<any> {
  const res = await apiClient.post<ApiResponse<any>>(`/comments/${commentId}/replies`, null, {
    params: { content, reply_to_user_id: replyToUserId },
  });
  return res.data.data;
}

// ============ 问答接口 ============

export async function fetchQuestions(shopId: number, page = 1, pageSize = 20): Promise<{ items: QuestionData[]; total: number }> {
  const res = await apiClient.get<ApiResponse<{ items: QuestionData[]; total: number }>>(`/shops/${shopId}/questions`, {
    params: { page, page_size: pageSize },
  });
  return res.data.data;
}

export async function postQuestion(shopId: number, title: string, content?: string): Promise<any> {
  const res = await apiClient.post<ApiResponse<any>>(`/shops/${shopId}/questions`, null, {
    params: { title, content },
  });
  return res.data.data;
}

export async function fetchAnswers(questionId: number): Promise<AnswerData[]> {
  const res = await apiClient.get<ApiResponse<AnswerData[]>>(`/questions/${questionId}/answers`);
  return res.data.data;
}

export async function postAnswer(questionId: number, content: string, replyToUserId?: number): Promise<any> {
  const res = await apiClient.post<ApiResponse<any>>(`/questions/${questionId}/answers`, null, {
    params: { content, reply_to_user_id: replyToUserId },
  });
  return res.data.data;
}

// ============ 点赞接口 ============

export async function toggleLike(entityType: string, entityId: number): Promise<{ is_liked: boolean; like_count: number }> {
  const res = await apiClient.post<ApiResponse<{ is_liked: boolean; like_count: number }>>('/likes/toggle', {
    entity_type: entityType,
    entity_id: entityId,
  });
  return res.data.data;
}
