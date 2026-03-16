/**
 * =============================================================================
 * Auth Context — User State Management
 * =============================================================================
 * React Context that holds the current user and provides login/logout.
 *
 * PATTERN: Context + Provider
 *   1. AuthProvider wraps the app (in layout.tsx)
 *   2. Any component calls useAuth() to get { user, login, logout, loading }
 *   3. On mount, AuthProvider calls GET /api/v1/auth/me to check if
 *      the user has a valid cookie — if yes, sets user state
 *
 * WHY CONTEXT instead of Redux/Zustand?
 *   For auth state, React Context is sufficient — auth changes rarely
 *   and doesn't cause performance issues. Redux is overkill here.
 * =============================================================================
 */
"use client";

import { createContext, useContext, useEffect, useState, useCallback, ReactNode } from "react";
import { useRouter } from "next/navigation";
import api from "@/lib/api";

// Types
interface User {
  id: string;
  email: string;
  display_name: string;
  avatar_url: string | null;
  created_at: string;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  fetchUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// =============================================================================
// AuthProvider — wraps the app
// =============================================================================
export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  // Fetch current user from BFF (uses httpOnly cookie)
  const fetchUser = useCallback(async () => {
    try {
      const res = await api.get("/api/v1/auth/me");
      setUser(res.data);
    } catch {
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  // On mount: check if user is already logged in (cookie exists + valid)
  useEffect(() => {
    fetchUser();
  }, [fetchUser]);

  // Login: POST credentials → BFF sets cookie → fetch user profile
  const login = useCallback(async (email: string, password: string) => {
    const res = await api.post("/api/v1/auth/login", { email, password });
    if (res.status === 200) {
      await fetchUser();      // Now cookie is set, fetch user data
      router.push("/dashboard");
    }
  }, [fetchUser, router]);

  // Logout: POST → BFF clears cookie → redirect to login
  const logout = useCallback(async () => {
    try {
      await api.post("/api/v1/auth/logout");
    } finally {
      setUser(null);
      router.push("/login");
    }
  }, [router]);

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, fetchUser }}>
      {children}
    </AuthContext.Provider>
  );
}

// =============================================================================
// useAuth hook — the consumer API
// =============================================================================
export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
