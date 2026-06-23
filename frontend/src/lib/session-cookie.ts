const SESSION_COOKIE = "tm_session=1; path=/; max-age=604800; SameSite=Lax";

export function hasSessionCookie(): boolean {
  if (typeof document === "undefined") return false;
  return document.cookie.split(";").some((part) => part.trim() === "tm_session=1");
}

export function setSessionCookie(): void {
  if (typeof document !== "undefined") {
    document.cookie = SESSION_COOKIE;
  }
}

export function clearSessionCookie(): void {
  if (typeof document !== "undefined") {
    document.cookie = "tm_session=; path=/; max-age=0; SameSite=Lax";
  }
}
