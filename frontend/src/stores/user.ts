import { defineStore } from 'pinia';

import { User } from '@/types/user';

interface UserState {
  profile: User | null;
  token: string;
}

export const useUserStore = defineStore('user', {
  state: (): UserState => ({
    profile: null,
    token: localStorage.getItem('token') ?? '',
  }),

  getters: {
    isAuthenticated: state => {
      try {
        if (state.token) {
          const arr = state.token.split('.');
          if (arr[1]) {
            const { exp } = JSON.parse(atob(arr[1]));
            const bufferTime = 86400000; // 1 day
            return Date.now() < exp * 1000 - bufferTime;
          }
        }
      } catch (_) { }
      return false;
    },
    displayName: (state) => {
      return state.profile?.full_name || 'Anonymous';
    }
  },

  actions: {
    updateProfile(updates: Partial<User>) {
      if (this.profile) {
        this.profile = { ...this.profile, ...updates };
      }
    },

    login(token: string, refreshToken?: string) {
      this.token = token;
      localStorage.setItem('token', token);
      if (refreshToken) {
        localStorage.setItem('refresh_token', refreshToken);
      }
    },

    clean() {
      this.token = '';
      this.profile = null;
      localStorage.removeItem('token');
      localStorage.removeItem('refresh_token');
    },

    logout() {
      this.clean();
      if (window.location.pathname === '/') {
        window.location.reload();
      } else {
        window.history.pushState(null, '', '/');
      }
    },
  },
});

