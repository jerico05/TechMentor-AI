"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { LogOut, Menu, Sparkles, X } from "lucide-react";
import * as React from "react";

import { APP_NAME } from "@/lib/constants";
import { logout } from "@/services/auth";
import { useAuthStore } from "@/store/auth-store";
import { cn } from "@/lib/utils";

const NAV = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/profile", label: "Profil" },
  { href: "/cv", label: "CV" },
  { href: "/github", label: "GitHub" },
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

  return (
    <header className="glass-card mb-6 flex animate-slide-down flex-wrap items-center justify-between gap-4 px-4 py-3 opacity-0 sm:px-6 sm:py-4">
      <div className="flex items-center gap-4">
        <Link
          href="/dashboard"
          className="group flex items-center gap-2 text-lg font-bold tracking-tight text-[hsl(var(--navy))] sm:text-xl"
        >
          <span className="flex h-8 w-8 items-center justify-center rounded-xl bg-gradient-to-br from-primary to-accent text-white shadow-md">
            <Sparkles className="h-4 w-4" />
          </span>
          <span className="hidden sm:inline">{APP_NAME}</span>
        </Link>
        <nav className="hidden items-center gap-0.5 lg:flex">
          {NAV.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={cn(pathname === item.href ? "nav-pill-active" : "nav-pill", "text-xs xl:text-sm")}
            >
              {item.label}
            </Link>
          ))}
        </nav>
      </div>

      <div className="flex items-center gap-2">
        <button
          type="button"
          className="rounded-xl p-2 lg:hidden"
          onClick={() => setMobileOpen(!mobileOpen)}
          aria-label="Menu"
        >
          {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </button>
        <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-primary to-primary/80 text-xs font-bold text-white">
          {initials}
        </div>
        <button
          type="button"
          onClick={handleLogout}
          className="rounded-xl p-2 text-muted-foreground hover:text-destructive"
          title="Déconnexion"
        >
          <LogOut className="h-5 w-5" />
        </button>
      </div>

      {mobileOpen && (
        <nav className="flex w-full flex-wrap gap-1 border-t border-white/50 pt-3 lg:hidden">
          {NAV.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              onClick={() => setMobileOpen(false)}
              className={cn(
                "rounded-xl px-3 py-2 text-sm",
                pathname === item.href ? "bg-[hsl(var(--navy))] text-white" : "hover:bg-white/60",
              )}
            >
              {item.label}
            </Link>
          ))}
        </nav>
      )}
    </header>
  );
}
