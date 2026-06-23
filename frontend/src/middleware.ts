import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const PROTECTED_PREFIXES = [
  "/dashboard",
  "/settings",
  "/profile",
  "/cv",
  "/github",
  "/analysis",
  "/roadmap",
  "/mentor",
  "/quiz",
  "/history",
  "/projects",
];

const AUTH_PATHS = ["/login", "/register", "/forgot-password"];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const hasSession = request.cookies.get("tm_session")?.value === "1";

  const isProtected = PROTECTED_PREFIXES.some((prefix) => pathname.startsWith(prefix));
  const isAuthPage = AUTH_PATHS.some((prefix) => pathname.startsWith(prefix));

  if (isProtected && !hasSession) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("next", pathname);
    return NextResponse.redirect(loginUrl);
  }

  if (isAuthPage && hasSession) {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    "/dashboard/:path*",
    "/settings/:path*",
    "/profile/:path*",
    "/cv/:path*",
    "/github/:path*",
    "/analysis/:path*",
    "/roadmap/:path*",
    "/mentor/:path*",
    "/quiz/:path*",
    "/history/:path*",
    "/projects/:path*",
    "/login",
    "/register",
    "/forgot-password",
  ],
};
