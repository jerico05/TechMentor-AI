"use client";

import { useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import * as React from "react";

import { runAppPrefetch } from "@/lib/prefetch-app";
import { useAppReady } from "@/lib/use-app-ready";
import type { AppRouterInstance } from "next/dist/shared/lib/app-router-context.shared-runtime";

/**
 * Preloads all app routes, page chunks and API data once per session.
 * Mounted in the app shell so the first click on any nav item is instant.
 */
export function AppPrefetcher() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const appReady = useAppReady();
  const didPrefetch = React.useRef(false);

  React.useEffect(() => {
    if (!appReady) {
      didPrefetch.current = false;
      return;
    }
    if (didPrefetch.current) return;
    didPrefetch.current = true;
    runAppPrefetch(router as Pick<AppRouterInstance, "prefetch">, queryClient);
  }, [appReady, queryClient, router]);

  return null;
}
