import Link from "next/link";
import { ArrowRight, Sparkles, Target, BrainCircuit, LineChart } from "lucide-react";

import { Button } from "@/components/ui/button";
import { APP_NAME } from "@/lib/constants";

const FEATURES = [
  {
    icon: Target,
    title: "Analyse de profil",
    description:
      "Extraction automatique de vos compétences depuis votre CV et votre GitHub pour identifier vos forces.",
  },
  {
    icon: LineChart,
    title: "Skill gap analysis",
    description:
      "Comparaison avec votre métier cible et score personnalisé pour suivre votre progression.",
  },
  {
    icon: BrainCircuit,
    title: "Mentor IA",
    description:
      "Un chatbot contextuel qui vous guide étape par étape dans votre apprentissage.",
  },
];

export default function HomePage() {
  return (
    <div className="flex min-h-screen flex-col bg-background">
      <main className="relative mx-auto flex w-full max-w-6xl flex-1 flex-col items-center px-4 py-12 text-center sm:py-20">
        <div className="crextio-shell w-full px-6 py-16 sm:px-12 sm:py-20">
          <div className="animate-fade-in inline-flex items-center gap-2 rounded-full bg-secondary/70 px-5 py-2.5 text-sm font-medium text-muted-foreground">
            <Sparkles className="h-4 w-4 text-primary" />
            <span>Plateforme de mentorat IA pour étudiants en informatique</span>
          </div>

          <h1 className="animate-slide-up stagger-1 mt-8 text-balance text-4xl font-light tracking-tight opacity-0 sm:text-5xl md:text-6xl">
            Devenez le développeur que vous voulez être avec{" "}
            <span className="font-extrabold text-[hsl(var(--navy))]">{APP_NAME}</span>
          </h1>

          <p className="animate-slide-up stagger-2 mx-auto mt-6 max-w-2xl text-pretty text-lg leading-relaxed text-muted-foreground opacity-0">
            Analysez votre profil, détectez vos lacunes, obtenez une roadmap personnalisée et
            échangez avec un mentor IA tout au long de votre parcours.
          </p>

          <div className="animate-slide-up stagger-3 mt-10 flex flex-wrap items-center justify-center gap-4 opacity-0">
            <Button asChild size="lg" variant="navy" className="px-8 text-base">
              <Link href="/register">
                Commencer gratuitement <ArrowRight className="h-4 w-4" />
              </Link>
            </Button>
            <Button asChild size="lg" variant="outline" className="px-8">
              <Link href="/login">Se connecter</Link>
            </Button>
          </div>

          <div className="mt-20 grid w-full gap-6 sm:grid-cols-3">
            {FEATURES.map(({ icon: Icon, title, description }, i) => {
              const stagger = ["stagger-4", "stagger-5", "stagger-6"][i];
              return (
                <div
                  key={title}
                  className={`glass-card-interactive animate-slide-up ${stagger} p-8 text-left opacity-0`}
                >
                  <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-2xl bg-primary/15 text-primary">
                    <Icon className="h-6 w-6" />
                  </div>
                  <h3 className="text-lg font-bold text-[hsl(var(--navy))]">{title}</h3>
                  <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{description}</p>
                </div>
              );
            })}
          </div>
        </div>
      </main>
    </div>
  );
}
