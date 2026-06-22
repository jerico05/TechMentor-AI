"use client";

import axios, { type AxiosError, type AxiosInstance, type InternalAxiosRequestConfig } from "axios";

import { getFirebaseIdToken } from "@/lib/firebase";
import type { ApiError } from "@/types";
import { API_BASE_URL } from "@/lib/constants";

/**
 * Pre-configured axios instance.
 *
 * - Base path is `/api/v1` (same-origin via the Next.js rewrite in dev).
 * - Request interceptor injects the Firebase ID token when available.
 */
export const api: AxiosInstance = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: { "Content-Type": "application/json" },
  withCredentials: true,
  timeout: 30_000,
});

api.interceptors.request.use(async (config: InternalAxiosRequestConfig) => {
  const token = await getFirebaseIdToken();
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
