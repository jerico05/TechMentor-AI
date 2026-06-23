"use client";

import { useRouter } from "next/navigation";
import * as React from "react";

import { useSessionCookie } from "@/lib/use-session-cookie";
import { useAuthStore } from "@/store/auth-store";

interface AuthGuardProps {
  children: React.ReactNode;
}

/**
 * Redirect unauthenticated users to /login after hydration.
 * Always renders children on first paint (middleware already protects routes).
 */
export function AuthGuard({ children }: AuthGuardProps) {
  const router = useRouter();
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const isLoading = useAuthStore((s) => s.isLoading);
  const hasHydrated = useAuthStore((s) => s._hasHydrated);
  const sessionActive = useSessionCookie();

  React.useEffect(() => {
    if (!hasHydrated) return;
    const allowed = isAuthenticated || sessionActive;
    if (!isLoading && !allowed) {
      router.replace("/login");
    }
  }, [hasHydrated, isAuthenticated, isLoading, sessionActive, router]);

  return <>{children}</>;
}
