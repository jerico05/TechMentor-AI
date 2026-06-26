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

function stripJsonContentTypeForFormData(config: InternalAxiosRequestConfig): void {
  if (config.data instanceof FormData && config.headers) {
    delete config.headers["Content-Type"];
    delete config.headers["content-type"];
  }
}

function normalizeAxiosFailure(error: AxiosError<ApiError>): ApiError & { status: number; isAxiosError: true } {
  const status = error.response?.status ?? 0;
  const data = error.response?.data;

  if (data && typeof data === "object" && "error" in data && typeof data.error === "object") {
    return { ...data, status, isAxiosError: true };
  }

  if (data && typeof data === "object" && "detail" in data) {
    const detail = (data as { detail: unknown }).detail;
    const message = Array.isArray(detail)
      ? detail
          .map((item) => {
            if (item && typeof item === "object" && "msg" in item) {
              return String((item as { msg: unknown }).msg);
            }
            return "";
          })
          .filter(Boolean)
          .join(" ")
      : String(detail);
    return {
      error: {
        code: "validation_error",
        message: message || "Les données envoyées sont invalides.",
      },
      status,
      isAxiosError: true,
    };
  }

  return {
    error: {
      code: error.code ?? "network_error",
      message: error.message || "Erreur réseau.",
    },
    status,
    isAxiosError: true,
  };
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

/** Long-running endpoints (LLM, CV parsing, roadmap generation). */
export const apiSlow: AxiosInstance = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: { "Content-Type": "application/json" },
  timeout: 60_000,
});

for (const client of [apiSlow]) {
  client.interceptors.request.use(async (config: InternalAxiosRequestConfig) => {
    stripJsonContentTypeForFormData(config);
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

  client.interceptors.response.use(
    (response) => response,
    (error: AxiosError<ApiError>) => Promise.reject(normalizeAxiosFailure(error)),
  );
}

api.interceptors.request.use(async (config: InternalAxiosRequestConfig) => {
  stripJsonContentTypeForFormData(config);
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
  (error: AxiosError<ApiError>) => Promise.reject(normalizeAxiosFailure(error)),
);

export function isApiError(payload: unknown): payload is ApiError & { status: number } {
  return (
    typeof payload === "object" &&
    payload !== null &&
    "error" in payload &&
    typeof (payload as { error: unknown }).error === "object"
  );
}
