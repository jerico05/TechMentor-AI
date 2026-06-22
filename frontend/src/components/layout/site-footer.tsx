import Link from "next/link";

import { APP_NAME } from "@/lib/constants";

/** Public landing footer. */
export function SiteFooter() {
  return (
    <footer className="border-t">
      <div className="container flex flex-col items-center justify-between gap-4 py-8 text-sm text-muted-foreground sm:flex-row">
        <p>
          © {new Date().getFullYear()} {APP_NAME}. Tous droits réservés.
        </p>
        <nav className="flex items-center gap-4">
          <Link href="/login" className="hover:text-foreground">
            Connexion
          </Link>
          <Link href="/register" className="hover:text-foreground">
            Inscription
          </Link>
          <a
            href="https://www.rodiumai.io/"
            target="_blank"
            rel="noreferrer"
            className="hover:text-foreground"
          >
            Propulsé par RodiumAI
          </a>
        </nav>
      </div>
    </footer>
  );
}
