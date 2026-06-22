"use client";

import * as React from "react";
import { QueryClient, QueryClientProvider, isServer } from "@tanstack/react-query";

import { makeQueryClient } from "@/lib/query-client";
import { AuthProvider } from "@/components/auth/auth-provider";

let browserQueryClient: QueryClient | undefined = undefined;

function getQueryClient() {
  if (isServer) {
    // Server: always make a new query client.
    return makeQueryClient();
  }
  // Browser: reuse the client across React renders.
  if (!browserQueryClient) browserQueryClient = makeQueryClient();
  return browserQueryClient;
}

/**
 * Wraps the app with all client-side providers.
 * Mounted once from `app/layout.tsx`.
 */
export function Providers({ children }: { children: React.ReactNode }) {
  const queryClient = getQueryClient();
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>{children}</AuthProvider>
    </QueryClientProvider>
  );
}
