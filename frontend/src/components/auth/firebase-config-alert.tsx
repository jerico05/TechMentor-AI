import { isFirebaseConfigured } from "@/lib/firebase";

/** Alerte affichée si les variables Firebase Web sont absentes. */
export function FirebaseConfigAlert() {
  if (isFirebaseConfigured()) return null;

  return (
    <div className="rounded-2xl bg-destructive/10 p-4 text-sm text-destructive">
      <p className="font-medium">Firebase n&apos;est pas configuré.</p>
      <p className="mt-2 text-destructive/90">
        Vérifiez <code className="text-xs">frontend/.env</code> ou{" "}
        <code className="text-xs">frontend/.env.local</code>, puis redémarrez le frontend.
      </p>
      <ul className="mt-2 list-inside list-disc space-y-1 break-all text-xs text-destructive/90">
        <li><code>NEXT_PUBLIC_FIREBASE_API_KEY</code></li>
        <li><code>NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID</code></li>
        <li><code>NEXT_PUBLIC_FIREBASE_APP_ID</code></li>
      </ul>
      <a
        href="https://console.firebase.google.com/project/techmentor-ai/settings/general"
        target="_blank"
        rel="noreferrer"
        className="mt-2 inline-block text-xs font-semibold underline"
      >
        Ouvrir la console Firebase
      </a>
    </div>
  );
}
