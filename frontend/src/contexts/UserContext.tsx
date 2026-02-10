import { createContext, useContext, useState, useEffect, ReactNode } from "react";
// Ensure this path is correct based on your project structure
import api from "@/lib/api"; 

// --- TYPES ---
type User = {
  id: number;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  token_balance?: number;
};

type RegisterPayload = {
  email: string;
  password: string;
  username: string;
  name?: string;
  first_name?: string;
  last_name?: string;
};

type UserContextType = {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>; // <--- FIXED SIGNATURE
  register: (payload: RegisterPayload) => Promise<void>;
  logout: () => void;
  refreshMe: () => Promise<void>;
};

const UserContext = createContext<UserContextType | undefined>(undefined);

export function UserProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  // --- ACTIONS ---

  const logout = () => {
    localStorage.removeItem("access");
    localStorage.removeItem("refresh");
    setUser(null);
  };

  const refreshMe = async () => {
    const token = localStorage.getItem("access");
    if (!token) {
      setLoading(false);
      return;
    }

    try {
      const response = await api.get("/me/", {
        headers: { Authorization: `Bearer ${token}` }
      });
      setUser(response.data);
    } catch (error) {
      console.error("Session expired or invalid:", error);
      logout();
    } finally {
      setLoading(false);
    }
  };

  // ✅ FIXED: Accepts two arguments (email, password) to match Auth.tsx
  const login = async (email: string, password: string) => {
    try {
      // ⚠️ CRITICAL MAPPING:
      // The frontend form calls it 'email', but the backend auth system needs 'username'.
      // We assume the user typed their username into the email field.
      const payload = {
        username: email, 
        password: password
      };

      console.log("📤 Sending Login Payload:", payload);

      const response = await api.post("/token/", payload);
      
      // Save tokens
      localStorage.setItem("access", response.data.access);
      localStorage.setItem("refresh", response.data.refresh);
      
      // Fetch user profile immediately
      await refreshMe();
      
    } catch (error: any) {
      console.error("Login Error:", error.response?.data);
      const msg = error.response?.data?.detail || "Invalid credentials";
      throw new Error(msg);
    }
  };

  const register = async (payload: RegisterPayload) => {
    try {
      // 1. Register
      await api.post("/register/", payload);
      
      // 2. Auto-Login using the username and password just created
      await login(payload.username, payload.password);
      
    } catch (error: any) {
      console.error("Register Error:", error.response?.data);
      const data = error.response?.data;
      const msg = typeof data === 'string' ? data : (data?.error || "Registration failed");
      throw new Error(msg);
    }
  };

  // --- INITIAL LOAD ---
  useEffect(() => {
    refreshMe();
  }, []);

  return (
    <UserContext.Provider value={{ user, loading, login, register, logout, refreshMe }}>
      {children}
    </UserContext.Provider>
  );
}

export function useUser() {
  const context = useContext(UserContext);
  if (context === undefined) {
    throw new Error("useUser must be used within a UserProvider");
  }
  return context;
}