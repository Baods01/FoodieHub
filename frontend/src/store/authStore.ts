import { create } from 'zustand';

interface AuthState {
  isLoggedIn: boolean;
  userId: number | null;
  userName: string;
  userAvatar: string | null;
  login: (user: { id: number; name: string; avatar: string | null }) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  isLoggedIn: false,
  userId: null,
  userName: '',
  userAvatar: null,

  login: (user) =>
    set({
      isLoggedIn: true,
      userId: user.id,
      userName: user.name,
      userAvatar: user.avatar,
    }),

  logout: () =>
    set({
      isLoggedIn: false,
      userId: null,
      userName: '',
      userAvatar: null,
    }),
}));
