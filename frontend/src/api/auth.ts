import type { ApiResponse } from '../types/common';
import apiClient from './client';

// ============ 类型定义 ============

export interface LoginRequest {
  type: 'username' | 'phone' | 'email';
  account: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  password: string;
  phone: string;
  email: string;
}

export interface LoginResponseData {
  access_token: string;
  token_type: string;
  user: UserInfo;
}

export interface UserInfo {
  id: number;
  username: string;
  phone: string;
  email: string;
  avatar: string | null;
  bio: string | null;
  role: number;
  created_at: string;
}

export interface UserUpdateData {
  avatar?: string;
  bio?: string;
  gender?: 'male' | 'female' | 'other';
}

// ============ 接口函数 ============

/** 登录 */
export async function loginApi(data: LoginRequest): Promise<LoginResponseData> {
  const res = await apiClient.post<ApiResponse<LoginResponseData>>('/users/login', data);
  return res.data.data;
}

/** 注册 */
export async function registerApi(data: RegisterRequest): Promise<UserInfo> {
  const res = await apiClient.post<ApiResponse<UserInfo>>('/users/register', data);
  return res.data.data;
}

/** 获取当前用户信息 */
export async function fetchCurrentUser(): Promise<UserInfo | null> {
  try {
    const res = await apiClient.get<ApiResponse<UserInfo>>('/users/me');
    return res.data.data;
  } catch {
    return null;
  }
}

/** 更新个人信息 */
export async function updateProfileApi(data: UserUpdateData): Promise<UserInfo> {
  const res = await apiClient.put<ApiResponse<UserInfo>>('/users/me', data);
  return res.data.data;
}
