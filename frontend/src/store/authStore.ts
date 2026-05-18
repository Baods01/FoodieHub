import { create } from 'zustand';
import { fetchCurrentUser } from '../api/auth';
import type { UserInfo } from '../api/auth';

interface AuthState {
  isLoggedIn: boolean;
  userId: number | null;
  userName: string;
  userAvatar: string | null;
  userEmail: string;
  userPhone: string;
  initialized: boolean;

  /** 登录成功：存 token + 设用户信息 */
  login: (token: string, user: UserInfo) => void;

  /** 退出：清 token + 清用户信息 */
  logout: () => void;

  /** 应用启动时从 localStorage 恢复 token 并验证 */
  init: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  isLoggedIn: false,
  userId: null,
  userName: '',
  userAvatar: null,
  userEmail: '',
  userPhone: '',
  initialized: false,

  login: (token, user) => {
    localStorage.setItem('foodiehub_token', token);
    set({
      isLoggedIn: true,
      userId: user.id,
      userName: user.username,
      userAvatar: user.avatar,
      userEmail: user.email,
      userPhone: user.phone,
    });
  },

  logout: () => {
    localStorage.removeItem('foodiehub_token');
    set({
      isLoggedIn: false,
      userId: null,
      userName: '',
      userAvatar: null,
      userEmail: '',
      userPhone: '',
    });
  },

  init: async () => {
    const token = localStorage.getItem('foodiehub_token');
    if (!token) {
      set({ initialized: true });
      return;
    }
    try {
      const user = await fetchCurrentUser();
      if (user) {
        set({
          isLoggedIn: true,
          userId: user.id,
          userName: user.username,
          userAvatar: user.avatar,
          userEmail: user.email,
          userPhone: user.phone,
        });
      } else {
        // Token 无效，清理
        localStorage.removeItem('foodiehub_token');
      }
    } catch {
      localStorage.removeItem('foodiehub_token');
    } finally {
      set({ initialized: true });
    }
  },
}));
