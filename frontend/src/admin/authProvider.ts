/**
 * react-admin authProvider 适配层
 *
 * 对接主站的 JWT 认证体系，复用 authStore。
 * login 调用 POST /users/login → 检查 role === 1 → 写入 authStore
 */
import { useAuthStore } from '../store/authStore';
import { loginApi } from '../api/auth';
import type { AuthProvider } from 'react-admin';

export const authProvider: AuthProvider = {
  login: async ({ username, password }: { username: string; password: string }) => {
    try {
      const result = await loginApi({
        account: username,
        password,
        type: 'username',
      });

      const { access_token, user } = result;

      // role 校验：仅管理员可访问后台
      if (user.role !== 1) {
        return Promise.reject(new Error('非管理员账号，无法访问后台'));
      }

      // 写入 authStore（同步主站登录状态）
      useAuthStore.getState().login(access_token, user);

      return Promise.resolve();
    } catch (err: any) {
      return Promise.reject(err?.message || '登录失败');
    }
  },

  logout: () => {
    useAuthStore.getState().logout();
    return Promise.resolve();
  },

  checkAuth: () => {
    const state = useAuthStore.getState();
    if (state.isLoggedIn && state.isAdmin()) {
      return Promise.resolve();
    }
    return Promise.reject({ redirectTo: '/admin/login' });
  },

  checkError: (error: any) => {
    const status = error?.status || error?.response?.status;
    if (status === 401 || status === 403) {
      useAuthStore.getState().logout();
      return Promise.reject({ redirectTo: '/admin/login' });
    }
    return Promise.resolve();
  },

  getPermissions: () => {
    const { userRole } = useAuthStore.getState();
    return Promise.resolve({ role: userRole });
  },
};
