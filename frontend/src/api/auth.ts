// 对接后端时取消注释:
// import type { ApiResponse } from '../types/common';
// import apiClient from './client';

// ============ 类型定义 ============

export interface LoginRequest {
  account: string;
  password: string;
  loginMode: 'username' | 'phone' | 'email';
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
  user: {
    id: number;
    username: string;
    phone: string;
    email: string;
    avatar: string | null;
    bio: string | null;
    role: number;
    created_at: string;
  };
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

export interface ApiError {
  code: number;
  message: string;
}

// ============ 接口函数 ============

/** 登录 */
export async function loginApi(data: LoginRequest): Promise<LoginResponseData> {
  // 对接后端时取消注释:
  // const formData = new URLSearchParams();
  // formData.append('username', data.username);
  // formData.append('password', data.password);
  // const res = await apiClient.post<LoginResponseData>('/users/login', formData, {
  //   headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  // });
  // return res.data;
  return mockLogin(data);
}

/** 注册 */
export async function registerApi(data: RegisterRequest): Promise<UserInfo> {
  // 对接后端时取消注释:
  // const res = await apiClient.post<ApiResponse<UserInfo>>('/users/register', data);
  // return res.data.data;
  return mockRegister(data);
}

/** 获取当前用户信息（用于 Token 初始化验证） */
export async function fetchCurrentUser(): Promise<UserInfo | null> {
  // 对接后端时取消注释:
  // try {
  //   const res = await apiClient.get<ApiResponse<UserInfo>>('/users/me');
  //   return res.data.data;
  // } catch {
  //   return null;
  // }
  return mockFetchCurrentUser();
}

// ============ Mock 实现 ============

const delay = (ms = 500) => new Promise((r) => setTimeout(r, ms));

// 模拟已注册用户数据库
interface RegRecord { password: string; user: UserInfo; }
const registeredUsers: RegRecord[] = [];

// 预置一个测试用户
registeredUsers.push({
  password: '123456',
  user: {
    id: 1,
    username: 'test',
    phone: '13800138000',
    email: 'test@scau.edu.cn',
    avatar: null,
    bio: '食探社测试用户',
    role: 0,
    created_at: new Date().toISOString(),
  },
});

async function mockLogin(data: LoginRequest): Promise<LoginResponseData> {
  await delay(600);

  // 根据登录模式查找匹配的用户
  let record: RegRecord | undefined;
  if (data.loginMode === 'username') {
    record = registeredUsers.find((r) => r.user.username === data.account);
  } else if (data.loginMode === 'phone') {
    record = registeredUsers.find((r) => r.user.phone === data.account);
  } else if (data.loginMode === 'email') {
    record = registeredUsers.find((r) => r.user.email === data.account.toLowerCase());
  }

  if (!record) {
    throw { code: 400, message: '账号或密码错误' };
  }
  if (record.password !== data.password) {
    throw { code: 400, message: '账号或密码错误' };
  }
  return {
    access_token: `mock_token_${record.user.username}_${Date.now()}`,
    token_type: 'bearer',
    user: record.user,
  };
}

async function mockRegister(data: RegisterRequest): Promise<UserInfo> {
  await delay(600);

  // 校验用户名
  if (data.username.length < 2 || data.username.length > 50) {
    throw { code: 400, message: '用户名长度应在 2-50 个字符之间' };
  }
  if (!/^[\w\u4e00-\u9fa5]+$/.test(data.username)) {
    throw { code: 400, message: '用户名只能包含字母、数字、下划线和中文' };
  }
  if (registeredUsers.some((r) => r.user.username === data.username)) {
    throw { code: 400, message: '该用户名已被注册' };
  }

  // 校验手机号
  if (!/^1[3-9]\d{9}$/.test(data.phone)) {
    throw { code: 400, message: '手机号格式不正确，请输入11位手机号' };
  }

  // 校验邮箱
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.email)) {
    throw { code: 400, message: '邮箱格式不正确' };
  }

  // 校验密码
  if (data.password.length < 6) {
    throw { code: 400, message: '密码长度不能少于 6 位' };
  }

  const newUser: UserInfo = {
    id: registeredUsers.length + 1,
    username: data.username,
    phone: data.phone,
    email: data.email,
    avatar: null,
    bio: null,
    role: 0,
    created_at: new Date().toISOString(),
  };

  registeredUsers.push({ password: data.password, user: newUser });
  return newUser;
}

async function mockFetchCurrentUser(): Promise<UserInfo | null> {
  // 从 localStorage 读取 token
  const token = localStorage.getItem('foodiehub_token');
  if (!token) return null;

  // Mock: token 格式为 "mock_token_username_timestamp"
  const match = token.match(/^mock_token_(.+)_\d+$/);
  if (!match) return null;

  const record = registeredUsers.find((r) => r.user.username === match[1]);
  if (!record) return null;

  return record.user;
}
