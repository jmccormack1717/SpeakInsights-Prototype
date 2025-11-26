/** Simple auth store for email/password login/signup */
import { create } from 'zustand';

interface AuthUser {
  userId: string;
  email: string;
  fullName?: string | null;
}

interface AuthState {
  user: AuthUser | null;
  token: string | null;
  isInitializing: boolean;
  setAuth: (user: AuthUser, token: string) => void;
  logout: () => void;
  initializeFromStorage: () => void;
}

const STORAGE_KEY = 'si-auth';

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: null,
  isInitializing: true,

  setAuth: (user, token) => {
    const payload = { user, token };
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
    set({ user, token });
  },

  logout: () => {
    window.localStorage.removeItem(STORAGE_KEY);
    set({ user: null, token: null });
  },

  initializeFromStorage: () => {
    try {
      const raw = window.localStorage.getItem(STORAGE_KEY);
      if (!raw) {
        set({ isInitializing: false });
        return;
      }
      const parsed = JSON.parse(raw) as { user: AuthUser; token: string };
      if (parsed?.user && parsed?.token) {
        set({
          user: parsed.user,
          token: parsed.token,
          isInitializing: false,
        });
      } else {
        set({ isInitializing: false });
      }
    } catch {
      set({ isInitializing: false });
    }
  },
}));


