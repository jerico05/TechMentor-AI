/** All authenticated app routes (prefetch on session start). */
export const APP_ROUTES = [
  "/dashboard",
  "/analysis",
  "/roadmap",
  "/projects",
  "/mentor",
  "/quiz",
  "/history",
  "/settings",
] as const;

export type AppRoute = (typeof APP_ROUTES)[number];
