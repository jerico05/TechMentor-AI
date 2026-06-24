"use client";

import { useSessionCookie } from "@/lib/use-session-cookie";
import { useAuthStore } from "@/store/auth-store";

/** True when Firebase is ready and protected API calls can start. */
export function useAppReady(): boolean {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const firebaseReady = useAuthStore((s) => s._firebaseReady);
  const cookieSession = useSessionCookie();
  return firebaseReady && (isAuthenticated || cookieSession);
}
