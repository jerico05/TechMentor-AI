export const APP_NAME = process.env.NEXT_PUBLIC_APP_NAME ?? "TechMentor AI";

/**
 * Base URL for browser API calls. Must stay empty in production (Vercel HTTPS).
 * The app calls same-origin `/api/v1/...`; the server proxies via BACKEND_URL.
 * Never set an `http://` EC2 URL here - browsers block mixed content.
 */
function resolveApiBaseUrl(): string {
  const configured = (process.env.NEXT_PUBLIC_API_BASE_URL ?? "").trim();
  if (!configured) return "";

  if (typeof window !== "undefined") {
    const isHttpsPage = window.location.protocol === "https:";
    const isInsecureApi = configured.startsWith("http://");
    if (isHttpsPage && isInsecureApi) {
      console.warn(
        "[TechMentor] NEXT_PUBLIC_API_BASE_URL=http://... est ignore en HTTPS. " +
          "Laissez cette variable vide sur Vercel et utilisez BACKEND_URL.",
      );
      return "";
    }
  }

  return configured.replace(/\/$/, "");
}

export const API_BASE_URL = resolveApiBaseUrl();

/** Map an API error code to a user-friendly French message. */
export const ERROR_MESSAGES: Record<string, string> = {
  unauthorized: "Vous devez être connecté pour effectuer cette action.",
  forbidden: "Vous n'avez pas la permission d'effectuer cette action.",
  not_found: "Ressource introuvable.",
  conflict: "Cette ressource existe déjà.",
  validation_error: "Les données saisies sont invalides.",
  rate_limited: "Trop de requêtes. Réessayez dans un instant.",
  internal_error: "Une erreur inattendue est survenue. Réessayez plus tard.",
};

export function describeError(code: string | undefined, fallback = "Erreur inconnue."): string {
  if (!code) return fallback;
  return ERROR_MESSAGES[code] ?? fallback;
}
