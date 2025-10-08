// src/contexts/UserContext.tsx
import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import api from "@/lib/api";

type User = {
  id: number;
  email: string;
  username: string;
  // Optional full name provided by backend at registration
  name?: string;
  first_name: string;
  last_name: string;
};

type RegisterPayload = {
  email: string;
  password: string;
  username: string;
  // Allow a single 'name' field (what user entered during signup) or first/last split
  name?: string;
  first_name?: string;
  last_name?: string;
  role?: "producer" | "consumer";
};

type Ctx = {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (payload: RegisterPayload) => Promise<void>;
  logout: () => void;
  refreshMe: () => Promise<void>;
};

const UserContext = createContext<Ctx | undefined>(undefined);

export function UserProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const persistUser = (u: User | null) => {
    if (u) localStorage.setItem("user", JSON.stringify(u));
    else localStorage.removeItem("user");
    setUser(u);
  };

  const refreshMe = async () => {
    const { data } = await api.get<User>("/me/");
    persistUser(data);
  };

  const login = async (email: string, password: string) => {
    // Try a few common token endpoints (our backend exposes /token/; some projects use /auth/token/)
    const tokenPaths = ["/token/", "/auth/token/"];
    // Try both payload shapes: SimpleJWT expects {username, password}, but some APIs accept {email, password}
    const payloads = [
      { username: email, password },
      { email, password },
    ];
    let tok: any = null;
    let lastError: any = null;
    for (const path of tokenPaths) {
      for (const body of payloads) {
        try {
          const resp = await api.post(path, body);
          tok = resp.data;
          break;
        } catch (e) {
          lastError = e;
          // try next payload or path
        }
      }
      if (tok) break;
    }
    if (!tok) {
      // Network error (CORS/origin or bad base URL) vs bad creds
      const isNetwork = !(lastError as any)?.response;
      const message = isNetwork
        ? "Network error: cannot reach API"
        : ((lastError as any)?.response?.status === 401
          ? "Invalid email or password"
          : `Auth token request failed`);
      throw new Error(message);
    }
    localStorage.setItem("access", tok.access);
    localStorage.setItem("refresh", tok.refresh);
    await refreshMe();
  };

  const register = async (payload: RegisterPayload) => {
    // Backend accepts only: email, username, password, first_name, last_name
    let { email, password, username, name, first_name, last_name } = payload;
    if (!first_name && !last_name && name) {
      const parts = name.trim().split(/\s+/, 2);
      first_name = parts[0] || "";
      last_name = parts[1] || "";
    }
    const body = { email, password, username, first_name: first_name || "", last_name: last_name || "" };
    try {
      await api.post("register/", body);
    } catch (err: any) {
      // Surface useful backend validation messages
      const data = err?.response?.data;
      const msg = typeof data === "string"
        ? data
        : (data?.detail || data?.email?.[0] || data?.username?.[0] || data?.password?.[0] || "Signup failed");
      throw new Error(msg);
    }
    await login(email, password);
  };

  const logout = () => {
    persistUser(null);
    localStorage.removeItem("access");
    localStorage.removeItem("refresh");
  };

  useEffect(() => {
    const access = localStorage.getItem("access");
    if (!access) {
      localStorage.removeItem("user");
      setLoading(false);
      return;
    }
    (async () => {
      try {
        await refreshMe();
      } catch {
        // token invalid
        logout();
      } finally {
        setLoading(false);
      }
    })();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <UserContext.Provider value={{ user, loading, login, register, logout, refreshMe }}>
      {children}
    </UserContext.Provider>
  );
}

export function useUser() {
  const ctx = useContext(UserContext);
  if (!ctx) throw new Error("useUser must be used within UserProvider");
  return ctx;
}
