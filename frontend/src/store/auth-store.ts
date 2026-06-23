"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";

import { clearSessionCookie } from "@/lib/session-cookie";
import { clearAuthTokenCache } from "@/services/api";
import type { UserPublic } from "@/types";

interface AuthState {
  user: UserPublic | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  _hasHydrated: boolean;
  setUser: (user: UserPublic | null) => void;
  setLoading: (loading: boolean) => void;
  setHasHydrated: (hydrated: boolean) => void;
  logout: () => void;
}

/**
 * Client auth state - Firebase holds tokens; we persist the backend user profile.
 */
export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,
      isLoading: true,
      _hasHydrated: false,
      setUser: (user) =>
        set({
          user,
          isAuthenticated: user !== null,
          isLoading: false,
        }),
      setLoading: (isLoading) => set({ isLoading }),
      setHasHydrated: (hydrated) => set({ _hasHydrated: hydrated }),
      logout: () => {
        clearSessionCookie();
        clearAuthTokenCache();
        set({
          user: null,
          isAuthenticated: false,
          isLoading: false,
        });
      },
    }),
    {
      name: "tm-auth",
      partialize: (state) => ({ user: state.user, isAuthenticated: state.isAuthenticated }),
      onRehydrateStorage: () => () => {
        useAuthStore.setState({ _hasHydrated: true, isLoading: false });
      },
    },
  ),
);
