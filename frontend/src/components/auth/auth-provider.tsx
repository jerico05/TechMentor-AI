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

  React.useEffect(() => {
    const unsubscribe = onAuthStateChanged(firebaseAuth, async (firebaseUser) => {
      if (!firebaseUser) {
        setUser(null);
        return;
      }
      try {
        const profile = await syncBackendSession();
        setUser(profile);
      } catch {
        setUser(null);
      }
    });
    return () => unsubscribe();
  }, [setUser]);

  return <>{children}</>;
}
