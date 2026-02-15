import { defineStore } from "pinia";
import { accountApi } from "../api";

const persist = (key, value) => {
  if (!value) {
    localStorage.removeItem(key);
    return;
  }
  localStorage.setItem(key, value);
};

export const useAuthStore = defineStore("auth", {
  state: () => ({
    user: null,
    token: localStorage.getItem("sessionToken"),
    expiresAt: localStorage.getItem("sessionTokenExpiresAt"),
    initialized: false,
  }),
  getters: {
    isAuthenticated: (state) => Boolean(state.user && state.token),
    role: (state) => state.user?.role ?? null,
  },
  actions: {
    setSession(payload) {
      this.user = payload.user;
      this.token = payload.token;
      this.expiresAt = payload.expires_at;
      persist("sessionToken", payload.token);
      persist("sessionTokenExpiresAt", payload.expires_at);
    },
    clearSession() {
      this.user = null;
      this.token = null;
      this.expiresAt = null;
      persist("sessionToken");
      persist("sessionTokenExpiresAt");
    },
    async login(credentials) {
      const data = await accountApi.login(credentials);
      this.setSession(data);
      return data;
    },
    async register(form) {
      const data = await accountApi.register(form);
      this.setSession(data);
      return data;
    },
    async fetchProfile() {
      const data = await accountApi.profile();
      this.user = data.user;
      this.initialized = true;
      return data;
    },
    async bootstrap() {
      if (this.initialized) return;
      if (!this.token) {
        this.initialized = true;
        return;
      }
      try {
        await this.fetchProfile();
      } catch (error) {
        this.clearSession();
        this.initialized = true;
      }
    },
    async logout() {
      try {
        await accountApi.logout();
      } catch (error) {
        // ignore
      }
      this.clearSession();
    },
  },
});
