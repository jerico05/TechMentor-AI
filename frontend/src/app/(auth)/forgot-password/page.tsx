"use client";

import Link from "next/link";
import * as React from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { Loader2, Mail } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { isFirebaseConfigured } from "@/lib/firebase";
import { formatAuthError, requestPasswordReset } from "@/services/auth";

const schema = z.object({
  email: z.string().email("Email invalide."),
});

type FormData = z.infer<typeof schema>;

export default function ForgotPasswordPage() {
  const [sent, setSent] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [loading, setLoading] = React.useState(false);
  const firebaseReady = isFirebaseConfigured();

  const { register, handleSubmit, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
  });

  async function onSubmit(data: FormData) {
    setError(null);
    setLoading(true);
    try {
      await requestPasswordReset(data.email);
      setSent(true);
    } catch (err) {
      setError(formatAuthError(err, "Impossible d'envoyer l'email de réinitialisation."));
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-background px-4 py-8">
      <div className="crextio-shell w-full max-w-md animate-scale-in p-6 opacity-0 sm:p-8">
        <div className="mb-6 text-center">
          <Mail className="mx-auto mb-3 h-10 w-10 text-primary" />
          <h1 className="text-2xl font-extrabold text-[hsl(var(--navy))]">Mot de passe oublié</h1>
          <p className="mt-2 text-sm text-muted-foreground">
            Entrez votre email pour recevoir un lien de réinitialisation.
          </p>
        </div>

        {sent ? (
          <div className="space-y-4 text-center">
            <p className="text-sm text-green-600">
              Si un compte existe avec cet email, un lien de réinitialisation a été envoyé.
            </p>
            <Link href="/login" className="text-sm font-semibold text-primary hover:underline">
              Retour à la connexion
            </Link>
          </div>
        ) : (
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            {!firebaseReady && (
              <p className="text-sm text-destructive">Firebase n&apos;est pas configuré.</p>
            )}
            <div className="space-y-1">
              <Label htmlFor="email">Email</Label>
              <Input id="email" type="email" autoComplete="email" {...register("email")} />
              {errors.email && <p className="text-xs text-destructive">{errors.email.message}</p>}
            </div>
            {error && <p className="text-sm text-destructive">{error}</p>}
            <Button type="submit" variant="navy" className="w-full" disabled={loading || !firebaseReady}>
              {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
              Envoyer le lien
            </Button>
            <p className="text-center text-sm text-muted-foreground">
              <Link href="/login" className="font-semibold text-primary">Retour à la connexion</Link>
            </p>
          </form>
        )}
      </div>
    </main>
  );
}
