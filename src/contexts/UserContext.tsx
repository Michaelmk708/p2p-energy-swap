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
    // Try a few common token endpoints (some backends expose /auth/token/ while others use /token/)
    const tokenPaths = ["/auth/token/", "/token/"];
    let tok: any = null;
    let lastError: any = null;
    for (const path of tokenPaths) {
      try {
        const resp = await api.post(path, { email, password });
        tok = resp.data;
        break;
      } catch (e) {
        lastError = e;
        // try next
      }
    }
    if (!tok) {
      throw lastError || new Error("Auth token request failed");
    }
    localStorage.setItem("access", tok.access);
    localStorage.setItem("refresh", tok.refresh);
    await refreshMe();
  };

  const register = async (payload: RegisterPayload) => {
    await api.post("/register/", payload);
    await login(payload.email, payload.password);
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
