"use client";

import { useRouter } from "next/navigation";
import * as React from "react";

import { useAuthStore } from "@/store/auth-store";

interface AuthGuardProps {
  children: React.ReactNode;
}

/** Redirect unauthenticated users to /login. */
export function AuthGuard({ children }: AuthGuardProps) {
  const router = useRouter();
  const { isAuthenticated, isLoading, user } = useAuthStore();

  React.useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.replace("/login");
    }
  }, [isAuthenticated, isLoading, router]);

  // Session déjà connue (login ou rehydratation) : accès immédiat.
  if (isAuthenticated && user) {
    return <>{children}</>;
  }

  if (isLoading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center text-sm text-muted-foreground">
        Chargement…
      </div>
    );
  }

  return null;
}
