"use client";

import * as React from "react";
import { onAuthStateChanged } from "firebase/auth";

import { getFirebaseAuth, getFirebaseIdToken, isFirebaseConfigured } from "@/lib/firebase";
import { clearSessionCookie, setSessionCookie } from "@/lib/session-cookie";
import { clearAuthTokenCache } from "@/services/api";
import { syncBackendSession } from "@/services/auth";
import { useAuthStore } from "@/store/auth-store";

/**
 * Listens to Firebase auth state and syncs the backend user profile.
 * Skips POST /auth/session when a cached profile already exists (fast path).
 */
export function AuthProvider({ children }: { children: React.ReactNode }) {
  const setUser = useAuthStore((s) => s.setUser);
  const setLoading = useAuthStore((s) => s.setLoading);

  React.useEffect(() => {
    if (!isFirebaseConfigured()) {
      clearSessionCookie();
      setUser(null);
      setLoading(false);
      return;
    }

    const unsubscribe = onAuthStateChanged(getFirebaseAuth(), async (firebaseUser) => {
      if (!firebaseUser) {
        clearSessionCookie();
        clearAuthTokenCache();
        setUser(null);
        return;
      }

      const cachedUser = useAuthStore.getState().user;
      if (cachedUser) {
        setSessionCookie();
        setLoading(false);
        void getFirebaseIdToken();
        void syncBackendSession()
          .then((profile) => setUser(profile))
          .catch(() => {});
        return;
      }

      try {
        const profile = await syncBackendSession();
        setSessionCookie();
        setUser(profile);
      } catch {
        clearSessionCookie();
        setUser(null);
      }
    });
    return () => unsubscribe();
  }, [setUser, setLoading]);

  return <>{children}</>;
}
