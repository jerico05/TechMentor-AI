import Link from "next/link";

import { APP_NAME } from "@/lib/constants";

/** Footer landing - style Crextio. */
export function SiteFooter() {
  return (
    <footer className="px-4 pb-8 pt-4 sm:px-8">
      <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-4 rounded-[2rem] bg-white px-6 py-6 text-sm text-muted-foreground shadow-[0_4px_24px_rgba(26,43,75,0.06)] sm:flex-row">
        <p>
          © {new Date().getFullYear()} {APP_NAME}. Tous droits réservés.
        </p>
        <nav className="flex items-center gap-4">
          <Link href="/login" className="rounded-full px-3 py-1 transition-colors hover:bg-secondary hover:text-foreground">
            Connexion
          </Link>
          <Link href="/register" className="rounded-full px-3 py-1 transition-colors hover:bg-secondary hover:text-foreground">
            Inscription
          </Link>
        </nav>
        <p className="text-muted-foreground">
          Propulsé par{" "}
          <a href="https://groq.com/" target="_blank" rel="noreferrer" className="hover:text-primary">
            Groq
          </a>{" "}
          &{" "}
          <a href="https://ai.google.dev/" target="_blank" rel="noreferrer" className="hover:text-primary">
            Gemini
          </a>
        </p>
      </div>
    </footer>
  );
}
