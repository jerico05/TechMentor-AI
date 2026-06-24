"use client";

import { QueryClient } from "@tanstack/react-query";

/** Single shared QueryClient with sensible defaults. */
export function makeQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 60 * 1000, // 1 min
        gcTime: 5 * 60 * 1000, // 5 min
        retry: 1,
        retryDelay: (attempt) => Math.min(1000 * 2 ** attempt, 10_000),
        refetchOnWindowFocus: false,
      },
      mutations: {
        retry: 0,
      },
    },
  });
}
