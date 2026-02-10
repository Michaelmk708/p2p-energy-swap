// src/lib/api.ts
/// <reference types="vite/client" />
import axios, { AxiosError, AxiosRequestConfig } from "axios";

// Resolve API base URL from .env or fallback to localhost:8000/api
const API_BASE = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api").replace(/\/+$/, "") + "/";

// Create axios instance
const api = axios.create({
  baseURL: API_BASE,
  headers: {
    "Content-Type": "application/json",
  },
});

// Attach access token if present
api.interceptors.request.use((config) => {
  if (typeof config.url === "string" && !/^https?:\/\//i.test(config.url)) {
    config.url = config.url.replace(/^\/+/, "");
  }

  const access = localStorage.getItem("access");
    if (!config.headers) {
  config.headers = new axios.AxiosHeaders(); // create proper AxiosHeaders object
  }


  return config;
});

// --- Token refresh logic
let isRefreshing = false;
let pendingRequests: Array<(token: string | null) => void> = [];

function subscribeTokenRefresh(cb: (token: string | null) => void) {
  pendingRequests.push(cb);
}

function onRefreshed(newToken: string | null) {
  pendingRequests.forEach((cb) => cb(newToken));
  pendingRequests = [];
}

// Response interceptor
api.interceptors.response.use(
  (res) => res,
  async (error: AxiosError) => {
    const original = error.config as AxiosRequestConfig & { _retry?: boolean };

    if (error.response?.status === 401 && !original?._retry) {
      original._retry = true;

      const refresh = localStorage.getItem("refresh");
      if (!refresh) {
        localStorage.removeItem("access");
        localStorage.removeItem("refresh");
        localStorage.removeItem("user");
        return Promise.reject(error);
      }

      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          subscribeTokenRefresh((newToken) => {
            if (!newToken) return reject(error);
            original.headers = original.headers ?? {};
            (original.headers as Record<string, string>).Authorization = `Bearer ${newToken}`;
            resolve(api(original));
          });
        });
      }

      isRefreshing = true;
      try {
        // Only the correct Django endpoint
        const resp = await axios.post(`${API_BASE}token/refresh/`, { refresh });
        const newAccess = (resp.data as any).access;
        if (!newAccess) throw new Error("No access token in refresh response");

        localStorage.setItem("access", newAccess);
        onRefreshed(newAccess);

        original.headers = original.headers ?? {};
        (original.headers as Record<string, string>).Authorization = `Bearer ${newAccess}`;
        return api(original);
      } catch (e) {
        localStorage.removeItem("access");
        localStorage.removeItem("refresh");
        localStorage.removeItem("user");
        onRefreshed(null);
        return Promise.reject(e);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);

export default api;

// Unauthenticated API helper
export const internalApi = (baseUrl: string) => {
  const instance = axios.create({ baseURL: baseUrl.replace(/\/+$/, "") });
  instance.interceptors.response.use((r) => r, (e) => Promise.reject(e));
  return instance;
};

// Export base URL for debugging
export { API_BASE };
