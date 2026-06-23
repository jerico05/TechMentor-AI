import Link from "next/link";

import { Button } from "@/components/ui/button";

export default function NotFound() {
  return (
    <div className="container flex min-h-[60vh] flex-col items-center justify-center gap-4 text-center">
      <h1 className="text-4xl font-extrabold text-[hsl(var(--navy))]">404</h1>
      <p className="max-w-md text-muted-foreground">Cette page n&apos;existe pas ou a été déplacée.</p>
      <Button asChild className="rounded-2xl">
        <Link href="/">Retour à l&apos;accueil</Link>
      </Button>
    </div>
  );
}
