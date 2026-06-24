"use client";

import { FirebaseError } from "firebase/app";
import {
  GithubAuthProvider,
  GoogleAuthProvider,
  createUserWithEmailAndPassword,
  sendPasswordResetEmail,
  signInWithEmailAndPassword,
  signInWithPopup,
  signOut,
  type User as FirebaseUser,
} from "firebase/auth";

import { getFirebaseAuth, getFirebaseIdToken } from "@/lib/firebase";
import { describeError } from "@/lib/constants";
import { api, clearAuthTokenCache, isApiError } from "@/services/api";
import type { UserPublic } from "@/types";

export interface SessionSyncInput {
  firstname?: string;
  lastname?: string;
}

/** Sync the Firebase session with the backend and return the local user profile. */
export async function syncBackendSession(
  profile?: SessionSyncInput,
  firebaseUser?: FirebaseUser,
): Promise<UserPublic> {
  const token = firebaseUser
    ? await firebaseUser.getIdToken(true)
    : await getFirebaseIdToken(true);
  if (!token) {
    throw new Error("Aucune session Firebase active.");
  }
  const { data } = await api.post<UserPublic>("/auth/session", profile ?? {}, {
    headers: { Authorization: `Bearer ${token}` },
    timeout: 45_000,
  });
  return data;
}

async function syncBackendSessionWithRetry(
  profile?: SessionSyncInput,
  firebaseUser?: FirebaseUser,
): Promise<UserPublic> {
  clearAuthTokenCache();
  let lastError: unknown;
  for (let attempt = 0; attempt < 2; attempt += 1) {
    if (attempt > 0) {
      await new Promise((resolve) => setTimeout(resolve, 600));
    }
    try {
      return await syncBackendSession(profile, firebaseUser);
    } catch (err) {
      lastError = err;
    }
  }
  throw lastError;
}

/** Fetch the current user profile from the backend. */
export async function fetchCurrentUser(): Promise<UserPublic> {
  const token = await getFirebaseIdToken();
  if (!token) {
    throw new Error("Aucune session Firebase active.");
  }
  const { data } = await api.get<UserPublic>("/auth/me", {
    headers: { Authorization: `Bearer ${token}` },
  });
  return data;
}

export async function registerWithEmail(
  email: string,
  password: string,
  firstname: string,
  lastname: string,
): Promise<{ firebaseUser: FirebaseUser; user: UserPublic }> {
  const credential = await createUserWithEmailAndPassword(getFirebaseAuth(), email, password);
  const user = await syncBackendSession({ firstname, lastname }, credential.user);
  return { firebaseUser: credential.user, user };
}

export async function loginWithEmail(
  email: string,
  password: string,
): Promise<{ firebaseUser: FirebaseUser; user: UserPublic }> {
  const credential = await signInWithEmailAndPassword(getFirebaseAuth(), email, password);
  const user = await syncBackendSession(undefined, credential.user);
  return { firebaseUser: credential.user, user };
}

export async function loginWithGoogle(): Promise<{ firebaseUser: FirebaseUser; user: UserPublic }> {
  const provider = new GoogleAuthProvider();
  provider.setCustomParameters({ prompt: "select_account" });
  const credential = await signInWithPopup(getFirebaseAuth(), provider);
  await credential.user.reload();
  const user = await syncBackendSessionWithRetry(undefined, credential.user);
  return { firebaseUser: credential.user, user };
}

export async function loginWithGithub(): Promise<{ firebaseUser: FirebaseUser; user: UserPublic }> {
  const provider = new GithubAuthProvider();
  provider.addScope("user:email");
  provider.addScope("read:user");
  const credential = await signInWithPopup(getFirebaseAuth(), provider);
  await credential.user.reload();
  const user = await syncBackendSessionWithRetry(undefined, credential.user);
  return { firebaseUser: credential.user, user };
}

export async function requestPasswordReset(email: string): Promise<void> {
  await sendPasswordResetEmail(getFirebaseAuth(), email);
}

export async function logout(): Promise<void> {
  await signOut(getFirebaseAuth());
}

/** Map Firebase error codes to French messages. */
export function mapFirebaseError(code: string): string {
  const messages: Record<string, string> = {
    "auth/email-already-in-use": "Cet email est déjà utilisé.",
    "auth/invalid-email": "Adresse email invalide.",
    "auth/weak-password": "Le mot de passe doit contenir au moins 6 caractères.",
    "auth/user-not-found": "Email ou mot de passe incorrect.",
    "auth/wrong-password": "Email ou mot de passe incorrect.",
    "auth/invalid-credential": "Email ou mot de passe incorrect.",
    "auth/popup-closed-by-user": "Connexion annulée.",
    "auth/popup-blocked": "La fenêtre de connexion a été bloquée. Autorisez les popups.",
    "auth/unauthorized-domain": "Domaine non autorisé dans Firebase (ajoutez localhost).",
    "auth/operation-not-allowed": "Ce mode de connexion n'est pas activé dans Firebase.",
    "auth/account-exists-with-different-credential":
      "Un compte existe déjà avec cet email via un autre fournisseur.",
  };
  return messages[code] ?? "Erreur d'authentification. Réessayez.";
}

/** Normalize Firebase, API and network errors for display. */
export function formatAuthError(err: unknown, fallback: string): string {
  if (err instanceof FirebaseError) {
    return mapFirebaseError(err.code);
  }

  if (!err || typeof err !== "object") return fallback;

  const e = err as {
    code?: string;
    message?: string;
    status?: number;
    error?: { code?: string; message?: string };
  };

  if (e.code?.startsWith("auth/")) {
    return mapFirebaseError(e.code);
  }

  if (isApiError(err)) {
    const apiMessage = err.error.message?.trim();
    if (apiMessage && err.error.code === "backend_unreachable") {
      return apiMessage;
    }
    if (apiMessage && err.error.code === "unauthorized" && apiMessage !== "unauthorized") {
      return apiMessage;
    }
    return describeError(err.error.code, err.error.message);
  }

  if (e.error?.message) {
    return describeError(e.error.code, e.error.message);
  }

  if (e.message?.includes("timeout") || e.code === "ECONNABORTED") {
    return "Le serveur met trop de temps à répondre. Vérifiez que le backend tourne (port 8000).";
  }

  if (e.message?.includes("Network Error") || e.status === 0) {
    if (typeof window !== "undefined" && window.location.hostname !== "localhost") {
      return "Impossible de joindre le backend. Vérifiez BACKEND_URL sur Vercel et le proxy /api.";
    }
    return "Impossible de joindre le backend. Lancez-le sur http://localhost:8000";
  }

  if (e.status === 404) {
    return "Endpoint API introuvable. Vérifiez que le backend TechMentor tourne sur le port 8000.";
  }

  if (e.message) {
    return e.message;
  }

  return fallback;
}
