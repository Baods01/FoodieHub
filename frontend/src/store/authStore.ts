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
  userBio: string | null;
  userGender: string | null;
  userCreatedAt: string;
  initialized: boolean;
  unreadCount: number;

  /** 登录成功：存 token + 设用户信息 */
  login: (token: string, user: UserInfo) => void;

  /** 退出：清 token + 清用户信息 */
  logout: () => void;

  /** 应用启动时从 localStorage 恢复 token 并验证 */
  init: () => Promise<void>;

  /** 当前是否为管理员（role === 1） */
  isAdmin: () => boolean;

  /** 编辑资料后更新本地用户信息 */
  updateProfile: (data: { avatar?: string | null; bio?: string | null; gender?: string | null }) => void;

  /** 设置未读消息数 */
  setUnreadCount: (count: number) => void;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  isLoggedIn: false,
  userId: null,
  userName: '',
  userRole: 0,
  userAvatar: null,
  userEmail: '',
  userPhone: '',
  userBio: null,
  userGender: null,
  userCreatedAt: '',
  initialized: false,
  unreadCount: 0,

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
      userBio: user.bio,
      userGender: user.gender,
      userCreatedAt: user.created_at,
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
      userBio: null,
      userGender: null,
      userCreatedAt: '',
    });
  },

  isAdmin: () => {
    return get().userRole === 1;
  },

  setUnreadCount: (count) => set({ unreadCount: count }),

  updateProfile: (data) => {
    const updates: Partial<AuthState> = {};
    if (data.avatar !== undefined) updates.userAvatar = data.avatar;
    if (data.bio !== undefined) updates.userBio = data.bio;
    if (data.gender !== undefined) updates.userGender = data.gender;
    set(updates);
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
          userBio: user.bio,
          userGender: user.gender,
          userCreatedAt: user.created_at,
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
