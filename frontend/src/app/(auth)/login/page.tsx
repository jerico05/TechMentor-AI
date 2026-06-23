"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import * as React from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";

import { Button } from "@/components/ui/button";
import { FirebaseConfigAlert } from "@/components/auth/firebase-config-alert";
import { OAuthProviderButtons } from "@/components/auth/oauth-provider-buttons";
import { Input } from "@/components/ui/input";
import { PasswordInput } from "@/components/ui/password-input";
import { Label } from "@/components/ui/label";
import { APP_NAME } from "@/lib/constants";
import { isFirebaseConfigured } from "@/lib/firebase";
import { setSessionCookie } from "@/lib/session-cookie";
import {
  loginWithEmail,
  loginWithGithub,
  loginWithGoogle,
  formatAuthError,
} from "@/services/auth";
import { useAuthStore } from "@/store/auth-store";

const loginSchema = z.object({
  email: z.string().email("Email invalide."),
  password: z.string().min(1, "Mot de passe requis."),
});

type LoginForm = z.infer<typeof loginSchema>;

export default function LoginPage() {
  const router = useRouter();
  const setUser = useAuthStore((s) => s.setUser);
  const [error, setError] = React.useState<string | null>(null);
  const [loading, setLoading] = React.useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginForm>({ resolver: zodResolver(loginSchema) });

  const firebaseReady = isFirebaseConfigured();

  async function onSubmit(data: LoginForm) {
    setError(null);
    setLoading(true);
    try {
      const { user } = await loginWithEmail(data.email, data.password);
      setSessionCookie();
      setUser(user);
      router.replace("/dashboard");
    } catch (err) {
      setError(formatAuthError(err, "Connexion impossible. Réessayez."));
    } finally {
      setLoading(false);
    }
  }

  async function handleOAuth(provider: "google" | "github") {
    setError(null);
    setLoading(true);
    try {
      const result =
        provider === "google" ? await loginWithGoogle() : await loginWithGithub();
      setSessionCookie();
      setUser(result.user);
      router.replace("/dashboard");
    } catch (err) {
      setError(formatAuthError(err, "Connexion OAuth impossible."));
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-background px-4 py-8">
      <div className="crextio-shell w-full max-w-md p-6 sm:p-8">
        <div className="mb-6 text-center">
          <h1 className="text-2xl font-extrabold tracking-tight text-[hsl(var(--navy))]">Connexion</h1>
          <p className="mt-2 text-sm text-muted-foreground">Reconnectez-vous à votre mentor IA.</p>
        </div>
        <div className="space-y-4">
          <FirebaseConfigAlert />

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-3">
            <div className="space-y-1">
              <Label htmlFor="email">Email</Label>
              <Input id="email" type="email" autoComplete="email" {...register("email")} />
              {errors.email && (
                <p className="text-xs text-destructive">{errors.email.message}</p>
              )}
            </div>
            <div className="space-y-1">
              <Label htmlFor="password">Mot de passe</Label>
              <PasswordInput
                id="password"
                autoComplete="current-password"
                {...register("password")}
              />
              {errors.password && (
                <p className="text-xs text-destructive">{errors.password.message}</p>
              )}
              <p className="text-right">
                <Link href="/forgot-password" className="text-xs font-medium text-primary hover:underline">
                  Mot de passe oublié ?
                </Link>
              </p>
            </div>
            {error && <p className="text-sm text-destructive">{error}</p>}
            <Button type="submit" variant="default" className="w-full" disabled={loading || !firebaseReady}>
              {loading ? "Connexion…" : "Se connecter"}
            </Button>
          </form>

          <OAuthProviderButtons
            disabled={loading || !firebaseReady}
            onGoogle={() => handleOAuth("google")}
            onGithub={() => handleOAuth("github")}
          />

          <div className="pt-2 text-center text-sm text-muted-foreground">
            Pas encore de compte ?{" "}
            <Link href="/register" className="font-semibold text-primary transition-colors hover:text-primary/80">
              Créer un compte
            </Link>
          </div>
        </div>
      </div>
      <p className="mt-6 text-center text-xs text-muted-foreground">
        © {new Date().getFullYear()} {APP_NAME}
      </p>
    </main>
  );
}
