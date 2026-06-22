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

import { firebaseAuth, getFirebaseIdToken } from "@/lib/firebase";
import { describeError } from "@/lib/constants";
import { api, isApiError } from "@/services/api";
import type { UserPublic } from "@/types";

export interface SessionSyncInput {
  firstname?: string;
  lastname?: string;
}

/** Évite les appels /auth/session concurrents (login + onAuthStateChanged). */
let syncInFlight: Promise<UserPublic> | null = null;
let lastSyncedUid: string | null = null;

async function resolveIdToken(firebaseUser?: FirebaseUser): Promise<string> {
  if (firebaseUser) {
    return firebaseUser.getIdToken(false);
  }
  const token = await getFirebaseIdToken(false);
  if (!token) {
    throw new Error("Aucune session Firebase active.");
  }
  return token;
}

/** Sync the Firebase session with the backend and return the local user profile. */
export async function syncBackendSession(
  profile?: SessionSyncInput,
  firebaseUser?: FirebaseUser,
): Promise<UserPublic> {
  const uid = firebaseUser?.uid ?? firebaseAuth.currentUser?.uid ?? null;
  if (uid && uid === lastSyncedUid && syncInFlight) {
    return syncInFlight;
  }

  if (syncInFlight) {
    return syncInFlight;
  }

  syncInFlight = (async () => {
    const token = await resolveIdToken(firebaseUser);
    const { data } = await api.post<UserPublic>("/auth/session", profile ?? {}, {
      headers: { Authorization: `Bearer ${token}` },
      timeout: 15_000,
    });
    lastSyncedUid = uid;
    return data;
  })();

  try {
    return await syncInFlight;
  } finally {
    syncInFlight = null;
  }
}

/** Réinitialise le cache de sync (déconnexion). */
export function resetAuthSyncCache(): void {
  syncInFlight = null;
  lastSyncedUid = null;
}

/** Fetch the current user profile from the backend. */
export async function fetchCurrentUser(): Promise<UserPublic> {
  const token = await getFirebaseIdToken();
  if (!token) {
    throw new Error("Aucune session Firebase active.");
  }
  const { data } = await api.get<UserPublic>("/auth/me", {
    headers: { Authorization: `Bearer ${token}` },
    timeout: 10_000,
  });
  return data;
}

export async function registerWithEmail(
  email: string,
  password: string,
  firstname: string,
  lastname: string,
): Promise<{ firebaseUser: FirebaseUser; user: UserPublic }> {
  const credential = await createUserWithEmailAndPassword(firebaseAuth, email, password);
  const user = await syncBackendSession({ firstname, lastname }, credential.user);
  return { firebaseUser: credential.user, user };
}

export async function loginWithEmail(
  email: string,
  password: string,
): Promise<{ firebaseUser: FirebaseUser; user: UserPublic }> {
  const credential = await signInWithEmailAndPassword(firebaseAuth, email, password);
  const user = await syncBackendSession(undefined, credential.user);
  return { firebaseUser: credential.user, user };
}

export async function loginWithGoogle(): Promise<{ firebaseUser: FirebaseUser; user: UserPublic }> {
  const provider = new GoogleAuthProvider();
  provider.setCustomParameters({ prompt: "select_account" });
  const credential = await signInWithPopup(firebaseAuth, provider);
  const user = await syncBackendSession(undefined, credential.user);
  return { firebaseUser: credential.user, user };
}

export async function loginWithGithub(): Promise<{ firebaseUser: FirebaseUser; user: UserPublic }> {
  const provider = new GithubAuthProvider();
  provider.addScope("user:email");
  provider.addScope("read:user");
  const credential = await signInWithPopup(firebaseAuth, provider);
  const user = await syncBackendSession(undefined, credential.user);
  return { firebaseUser: credential.user, user };
}

export async function requestPasswordReset(email: string): Promise<void> {
  await sendPasswordResetEmail(firebaseAuth, email);
}

export async function logout(): Promise<void> {
  resetAuthSyncCache();
  await signOut(firebaseAuth);
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
    return describeError(err.error.code, err.error.message);
  }

  if (e.error?.message) {
    return describeError(e.error.code, e.error.message);
  }

  if (e.message?.includes("Network Error") || e.status === 0) {
    return "Impossible de joindre le backend. Lancez-le sur http://localhost:8001";
  }

  if (e.code === "ECONNABORTED" || e.message?.includes("timeout")) {
    return "Le serveur met trop de temps à répondre. Vérifiez que le backend est démarré.";
  }

  if (e.status === 404) {
    return "Endpoint API introuvable — vérifiez que le backend TechMentor tourne sur le port 8001 (pas une autre app sur 8000).";
  }

  if (e.message) {
    return e.message;
  }

  return fallback;
}
