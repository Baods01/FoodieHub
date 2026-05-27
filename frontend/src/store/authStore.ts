import { create } from 'zustand';
import { fetchCurrentUser } from '../api/auth';
import type { UserInfo } from '../api/auth';

interface AuthState {
  isLoggedIn: boolean;
  userId: number | null;
  userName: string;
  userRole: number;
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

  /** 当前是否为管理员（role === 1） */
  isAdmin: () => boolean;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  isLoggedIn: false,
  userId: null,
  userName: '',
  userRole: 0,
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
      userRole: user.role,
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
      userRole: 0,
      userAvatar: null,
      userEmail: '',
      userPhone: '',
    });
  },

  isAdmin: () => {
    return get().userRole === 1;
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
          userRole: user.role,
          userAvatar: user.avatar,
          userEmail: user.email,
          userPhone: user.phone,
        });
      } else {
        localStorage.removeItem('foodiehub_token');
      }
    } catch {
      localStorage.removeItem('foodiehub_token');
    } finally {
      set({ initialized: true });
    }
  },
}));
