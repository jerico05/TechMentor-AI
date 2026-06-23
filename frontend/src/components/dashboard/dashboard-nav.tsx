"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { LogOut, Menu, Settings, Sparkles, X } from "lucide-react";
import * as React from "react";

import { APP_ROUTES } from "@/lib/app-routes";
import { APP_NAME } from "@/lib/constants";
import { logout } from "@/services/auth";
import { useAuthStore } from "@/store/auth-store";
import { cn } from "@/lib/utils";

const NAV = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/analysis", label: "Analyse" },
  { href: "/roadmap", label: "Roadmap" },
  { href: "/projects", label: "Projets" },
  { href: "/mentor", label: "Mentor" },
  { href: "/quiz", label: "Quiz" },
  { href: "/history", label: "Historique" },
] as const;

export function DashboardNav() {
  const pathname = usePathname();
  const router = useRouter();
  const user = useAuthStore((s) => s.user);
  const storeLogout = useAuthStore((s) => s.logout);
  const [mobileOpen, setMobileOpen] = React.useState(false);

  async function handleLogout() {
    await logout();
    storeLogout();
    router.push("/login");
  }

  const initials = user
    ? `${user.firstname[0] ?? ""}${user.lastname[0] ?? ""}`.toUpperCase()
    : "?";

  const isActive = (href: string) =>
    pathname === href || (href !== "/dashboard" && pathname.startsWith(href));

  const navRef = React.useRef<HTMLElement>(null);

  React.useEffect(() => {
    const root = navRef.current;
    if (!root) return;
    const activeEl = root.querySelector<HTMLElement>('[data-nav-active="true"]');
    activeEl?.scrollIntoView({ behavior: "instant", block: "nearest", inline: "nearest" });
  }, [pathname]);

  return (
    <header>
      <div className="flex items-center justify-between gap-4">
        {/* Logo */}
        <Link
          href="/dashboard"
          prefetch
          className="group flex shrink-0 items-center gap-2.5 text-lg font-bold tracking-tight text-[hsl(var(--navy))]"
        >
          <span className="flex h-9 w-9 items-center justify-center rounded-2xl bg-[hsl(var(--navy))] text-white shadow-md shadow-navy/20">
            <Sparkles className="h-4 w-4" />
          </span>
          <span className="hidden sm:inline">{APP_NAME}</span>
        </Link>

        {/* Nav centrale — flex-wrap, sans overflow qui coupe les coins arrondis */}
        <nav ref={navRef} className="hidden min-w-0 flex-1 justify-center overflow-visible px-2 py-1 lg:flex">
          <div className="nav-pill-track mx-auto w-full max-w-4xl">
            {NAV.map((item) => {
              const active = isActive(item.href);
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  prefetch
                  data-nav-active={active ? "true" : undefined}
                  className={cn(
                    active ? "nav-pill-active" : "nav-pill",
                    "text-xs xl:text-sm",
                  )}
                >
                  {item.label}
                </Link>
              );
            })}
          </div>
        </nav>

        {/* Actions droite */}
        <div className="flex shrink-0 items-center gap-1 sm:gap-2">
          <Link
            href="/settings"
            prefetch
            className={cn(
              "hidden rounded-full p-2.5 transition-colors sm:inline-flex",
              pathname.startsWith("/settings")
                ? "bg-[hsl(var(--navy))] text-white shadow-md shadow-navy/20"
                : "text-muted-foreground hover:bg-secondary/80 hover:text-foreground",
            )}
            aria-label="Paramètres"
          >
            <Settings className="h-5 w-5" />
          </Link>

          <div
            className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-primary to-primary/80 text-xs font-bold text-white shadow-md"
            title={user ? `${user.firstname} ${user.lastname}` : "Profil"}
          >
            {initials}
          </div>

          <button
            type="button"
            onClick={handleLogout}
            className="hidden rounded-full p-2.5 text-muted-foreground transition-colors hover:bg-destructive/10 hover:text-destructive md:inline-flex"
            title="Déconnexion"
          >
            <LogOut className="h-5 w-5" />
          </button>

          <button
            type="button"
            className="rounded-full p-2.5 text-muted-foreground transition-colors hover:bg-secondary/80 lg:hidden"
            onClick={() => setMobileOpen(!mobileOpen)}
            aria-label="Menu"
          >
            {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </div>
      </div>

      {mobileOpen && (
        <nav className="mt-4 flex flex-wrap gap-1.5 border-t border-border/60 pt-4 lg:hidden">
          {NAV.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              prefetch
              onClick={() => setMobileOpen(false)}
              className={cn(
                "rounded-full px-3.5 py-2 text-sm",
                isActive(item.href)
                  ? "bg-[hsl(var(--navy))] font-semibold text-white"
                  : "bg-secondary/60 text-muted-foreground hover:bg-secondary",
              )}
            >
              {item.label}
            </Link>
          ))}
          <Link
            href="/settings"
            prefetch
            onClick={() => setMobileOpen(false)}
            className={cn(
              "inline-flex items-center gap-2 rounded-full px-3.5 py-2 text-sm",
              pathname.startsWith("/settings")
                ? "bg-[hsl(var(--navy))] font-semibold text-white"
                : "bg-secondary/60 text-muted-foreground hover:bg-secondary",
            )}
          >
            <Settings className="h-4 w-4" />
            Paramètres
          </Link>
          <button
            type="button"
            onClick={() => {
              setMobileOpen(false);
              void handleLogout();
            }}
            className="inline-flex items-center gap-2 rounded-full bg-destructive/10 px-3.5 py-2 text-sm font-medium text-destructive hover:bg-destructive/15"
          >
            <LogOut className="h-4 w-4" />
            Déconnexion
          </button>
        </nav>
      )}
    </header>
  );
}
