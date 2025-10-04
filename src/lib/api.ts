// src/lib/api.ts
/// <reference types="vite/client" />
import axios, { AxiosError, AxiosRequestConfig } from "axios";

// Safely read the base URL from Vite env, fall back to localhost
const API_BASE: string =
  (typeof import.meta !== "undefined" &&
    (import.meta as any)?.env?.VITE_API_BASE_URL) ||
  "http://localhost:8000/api";

// Create the axios instance
const api = axios.create({
  baseURL: API_BASE.replace(/\/+$/, ""), // trim trailing slash
});

// --- Request interceptor: attach Authorization header if we have a token
api.interceptors.request.use((config) => {
  const access = localStorage.getItem("access");
  if (access) {
    if (!config.headers) {
      config.headers = {} as import("axios").AxiosRequestHeaders;
    }
    // Axios v1+ uses AxiosHeaders, but we can safely set Authorization like this:
    (config.headers as any).Authorization = `Bearer ${access}`;
  }
  return config;
});

// --- Simple refresh-lock so multiple 401s don’t spam the refresh endpoint
let isRefreshing = false;
let pendingRequests: Array<(token: string | null) => void> = [];

function subscribeTokenRefresh(cb: (token: string | null) => void) {
  pendingRequests.push(cb);
}

function onRefreshed(newToken: string | null) {
  pendingRequests.forEach((cb) => cb(newToken));
  pendingRequests = [];
}

// --- Response interceptor: try refresh on 401 once
api.interceptors.response.use(
  (res) => res,
  async (error: AxiosError) => {
    const original = error.config as AxiosRequestConfig & { _retry?: boolean };

    if (error.response?.status === 401 && !original?._retry) {
      original._retry = true;

      const refresh = localStorage.getItem("refresh");
      if (!refresh) {
        // No refresh token—we can’t recover
        localStorage.removeItem("access");
        localStorage.removeItem("refresh");
        localStorage.removeItem("user");
        return Promise.reject(error);
      }

      // If a refresh is already running, queue this request
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

      // Start a refresh
      isRefreshing = true;
      try {
        // Try a couple of common refresh endpoints
        const refreshPaths = ["/auth/token/refresh/", "/token/refresh/"];
        let resp: any = null;
        let refreshError: any = null;
        for (const p of refreshPaths) {
          try {
            resp = await axios.post(`${API_BASE.replace(/\/+$/, "")}${p}`, { refresh });
            break;
          } catch (e) {
            refreshError = e;
          }
        }
        if (!resp) throw refreshError || new Error("Refresh request failed");
        const newAccess = (resp.data as any)?.access as string | undefined;

        if (!newAccess) {
          throw new Error("No access token in refresh response");
        }

        localStorage.setItem("access", newAccess);
        onRefreshed(newAccess);
        // Retry original request with new token
        original.headers = original.headers ?? {};
        (original.headers as Record<string, string>).Authorization = `Bearer ${newAccess}`;
        return api(original);
      } catch (e) {
        // Refresh failed -> clear auth
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
