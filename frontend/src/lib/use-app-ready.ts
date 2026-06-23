"use client";

import { useSessionCookie } from "@/lib/use-session-cookie";
import { useAuthStore } from "@/store/auth-store";

/** True when protected API calls can start (persisted user or session cookie). */
export function useAppReady(): boolean {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const cookieSession = useSessionCookie();
  return isAuthenticated || cookieSession;
}
