import type { Metadata } from "next";

import { Providers } from "@/app/providers";
import { APP_NAME } from "@/lib/constants";
import { fontClassName } from "@/lib/fonts";
import { cn } from "@/lib/utils";
import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: `${APP_NAME} — Mentor IA pour étudiants en informatique`,
    template: `%s · ${APP_NAME}`,
  },
  description:
    "Analysez votre profil, identifiez vos lacunes, obtenez une roadmap personnalisée et échangez avec un mentor IA.",
  applicationName: APP_NAME,
  authors: [{ name: "TechMentor AI" }],
  keywords: ["mentor IA", "carrière", "informatique", "roadmap", "étudiant", "RAG"],
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fr" suppressHydrationWarning>
      <body className={cn(fontClassName, "min-h-screen antialiased")}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
