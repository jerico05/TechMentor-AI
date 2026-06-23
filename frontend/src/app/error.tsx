"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

import { Button } from "@/components/ui/button";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  const router = useRouter();

  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <div className="container flex min-h-[60vh] flex-col items-center justify-center gap-4 text-center">
      <h1 className="text-2xl font-bold text-[hsl(var(--navy))]">Une erreur est survenue</h1>
      <p className="max-w-md text-sm text-muted-foreground">
        {error.message || "Impossible de charger cette page."}
      </p>
      <div className="flex gap-3">
        <Button onClick={() => reset()} className="rounded-2xl">Réessayer</Button>
        <Button variant="outline" onClick={() => router.push("/dashboard")} className="rounded-2xl">
          Retour au tableau de bord
        </Button>
      </div>
    </div>
  );
}
