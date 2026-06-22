"use client";

import * as React from "react";
import { onAuthStateChanged } from "firebase/auth";

import { firebaseAuth } from "@/lib/firebase";
import { syncBackendSession } from "@/services/auth";
import { useAuthStore } from "@/store/auth-store";

/**
 * Listens to Firebase auth state and syncs the backend user profile.
 */
export function AuthProvider({ children }: { children: React.ReactNode }) {
  const setUser = useAuthStore((s) => s.setUser);
  const setLoading = useAuthStore((s) => s.setLoading);

  React.useEffect(() => {
    const finishHydration = () => {
      const { isAuthenticated, user } = useAuthStore.getState();
      if (isAuthenticated && user) {
        setLoading(false);
      }
    };

    finishHydration();
    const unsubHydration = useAuthStore.persist.onFinishHydration(finishHydration);

    const unsubscribe = onAuthStateChanged(firebaseAuth, async (firebaseUser) => {
      if (!firebaseUser) {
        setUser(null);
        return;
      }

      const { isAuthenticated, user } = useAuthStore.getState();
      if (isAuthenticated && user) {
        setLoading(false);
        return;
      }

      try {
        const profile = await syncBackendSession(undefined, firebaseUser);
        setUser(profile);
      } catch {
        if (!useAuthStore.getState().isAuthenticated) {
          setUser(null);
        } else {
          setLoading(false);
        }
      }
    });

    return () => {
      unsubHydration();
      unsubscribe();
    };
  }, [setUser, setLoading]);

  return <>{children}</>;
}
