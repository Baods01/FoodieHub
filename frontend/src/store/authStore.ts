import { create } from 'zustand';

interface AuthState {
  isLoggedIn: boolean;
  userId: number | null;
  userName: string;
  userAvatar: string | null;
}

export const useAuthStore = create<AuthState>(() => ({
  isLoggedIn: false,
  userId: null,
  userName: '',
  userAvatar: null,
}));
