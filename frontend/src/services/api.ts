"use client";

import axios, { type AxiosError, type AxiosInstance, type InternalAxiosRequestConfig } from "axios";

import { getFirebaseIdToken } from "@/lib/firebase";
import type { ApiError } from "@/types";
import { API_BASE_URL } from "@/lib/constants";

let cachedToken: string | null = null;
let cacheUntil = 0;

async function resolveAuthToken(): Promise<string | null> {
  const now = Date.now();
  if (cachedToken && cacheUntil > now) {
    return cachedToken;
  }
  const token = await getFirebaseIdToken();
  if (token) {
    cachedToken = token;
    cacheUntil = now + 55_000;
  } else {
    cachedToken = null;
    cacheUntil = 0;
  }
  return token;
}

export function clearAuthTokenCache(): void {
  cachedToken = null;
  cacheUntil = 0;
}

/**
 * Pre-configured axios instance.
 *
 * - Base path is `/api/v1` (same-origin via the Next.js rewrite in dev).
 * - Request interceptor injects the Firebase ID token when available.
 */
export const api: AxiosInstance = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: { "Content-Type": "application/json" },
  timeout: 15_000,
});

api.interceptors.request.use(async (config: InternalAxiosRequestConfig) => {
  const existingAuth = config.headers?.Authorization ?? config.headers?.authorization;
  if (existingAuth) {
    return config;
  }
  const token = await resolveAuthToken();
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiError>) => {
    const normalized: ApiError = error.response?.data ?? {
      error: {
        code: error.code ?? "network_error",
        message: error.message || "Erreur réseau.",
      },
    };
    return Promise.reject({
      ...normalized,
      status: error.response?.status ?? 0,
      isAxiosError: true,
    });
  },
);

export function isApiError(payload: unknown): payload is ApiError & { status: number } {
  return (
    typeof payload === "object" &&
    payload !== null &&
    "error" in payload &&
    typeof (payload as { error: unknown }).error === "object"
  );
}
