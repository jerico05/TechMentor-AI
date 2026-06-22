export const APP_NAME = process.env.NEXT_PUBLIC_APP_NAME ?? "TechMentor AI";

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "";

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
