"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import * as React from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { isFirebaseConfigured } from "@/lib/firebase";
import {
  loginWithGithub,
  loginWithGoogle,
  formatAuthError,
  registerWithEmail,
} from "@/services/auth";
import { useAuthStore } from "@/store/auth-store";

const registerSchema = z
  .object({
    firstname: z.string().min(1, "Prénom requis."),
    lastname: z.string().min(1, "Nom requis."),
    email: z.string().email("Email invalide."),
    password: z.string().min(8, "Minimum 8 caractères."),
    confirmPassword: z.string().min(1, "Confirmation requise."),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Les mots de passe ne correspondent pas.",
    path: ["confirmPassword"],
  });

type RegisterForm = z.infer<typeof registerSchema>;

export default function RegisterPage() {
  const router = useRouter();
  const setUser = useAuthStore((s) => s.setUser);
  const [error, setError] = React.useState<string | null>(null);
  const [loading, setLoading] = React.useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterForm>({ resolver: zodResolver(registerSchema) });

  const firebaseReady = isFirebaseConfigured();

  async function onSubmit(data: RegisterForm) {
    setError(null);
    setLoading(true);
    try {
      const { user } = await registerWithEmail(
        data.email,
        data.password,
        data.firstname,
        data.lastname,
      );
      setUser(user);
      router.replace("/dashboard");
      return;
    } catch (err) {
      setError(formatAuthError(err, "Inscription impossible. Réessayez."));
      setLoading(false);
    }
  }

  async function handleOAuth(provider: "google" | "github") {
    setError(null);
    setLoading(true);
    try {
      const result =
        provider === "google" ? await loginWithGoogle() : await loginWithGithub();
      setUser(result.user);
      router.replace("/dashboard");
      return;
    } catch (err) {
      setError(formatAuthError(err, "Inscription OAuth impossible."));
      setLoading(false);
    }
  }

  return (
    <main className="mx-auto flex min-h-[85vh] max-w-md flex-col justify-center px-4 py-8">
      <div className="glass-card animate-scale-in p-8 opacity-0 shadow-[0_20px_60px_rgba(15,23,42,0.08)]">
        <div className="mb-6 text-center">
          <h1 className="text-2xl font-extrabold tracking-tight text-[hsl(var(--navy))]">Créer un compte</h1>
          <p className="mt-2 text-sm text-muted-foreground">Lancez votre mentorat en moins d&apos;une minute.</p>
        </div>
        <div className="space-y-4">
          {!firebaseReady && (
            <p className="rounded-md bg-destructive/10 p-3 text-sm text-destructive">
              Firebase n&apos;est pas configuré. Renseignez les variables{" "}
              <code className="text-xs">NEXT_PUBLIC_FIREBASE_*</code> dans{" "}
              <code className="text-xs">.env.local</code>.
            </p>
          )}

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-3">
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1">
                <Label htmlFor="firstname">Prénom</Label>
                <Input id="firstname" autoComplete="given-name" {...register("firstname")} />
                {errors.firstname && (
                  <p className="text-xs text-destructive">{errors.firstname.message}</p>
                )}
              </div>
              <div className="space-y-1">
                <Label htmlFor="lastname">Nom</Label>
                <Input id="lastname" autoComplete="family-name" {...register("lastname")} />
                {errors.lastname && (
                  <p className="text-xs text-destructive">{errors.lastname.message}</p>
                )}
              </div>
            </div>
            <div className="space-y-1">
              <Label htmlFor="email">Email</Label>
              <Input id="email" type="email" autoComplete="email" {...register("email")} />
              {errors.email && (
                <p className="text-xs text-destructive">{errors.email.message}</p>
              )}
            </div>
            <div className="space-y-1">
              <Label htmlFor="password">Mot de passe</Label>
              <Input
                id="password"
                type="password"
                autoComplete="new-password"
                {...register("password")}
              />
              {errors.password && (
                <p className="text-xs text-destructive">{errors.password.message}</p>
              )}
            </div>
            <div className="space-y-1">
              <Label htmlFor="confirmPassword">Confirmer le mot de passe</Label>
              <Input
                id="confirmPassword"
                type="password"
                autoComplete="new-password"
                {...register("confirmPassword")}
              />
              {errors.confirmPassword && (
                <p className="text-xs text-destructive">{errors.confirmPassword.message}</p>
              )}
            </div>
            {error && <p className="text-sm text-destructive">{error}</p>}
            <Button type="submit" className="w-full" disabled={loading || !firebaseReady}>
              {loading ? "Création…" : "Créer mon compte"}
            </Button>
          </form>

          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <span className="w-full border-t" />
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-card px-2 text-muted-foreground">ou</span>
            </div>
          </div>

          <Button
            type="button"
            variant="outline"
            className="w-full"
            disabled={loading || !firebaseReady}
            onClick={() => handleOAuth("google")}
          >
            S&apos;inscrire avec Google
          </Button>
          <Button
            type="button"
            variant="outline"
            className="w-full"
            disabled={loading || !firebaseReady}
            onClick={() => handleOAuth("github")}
          >
            S&apos;inscrire avec GitHub
          </Button>

          {error && <p className="text-sm text-destructive">{error}</p>}

          <div className="pt-2 text-center text-sm text-muted-foreground">
            Déjà inscrit ?{" "}
            <Link href="/login" className="font-semibold text-primary transition-colors hover:text-primary/80">
              Se connecter
            </Link>
          </div>
        </div>
      </div>
    </main>
  );
}
