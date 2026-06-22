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
    <main className="relative mx-auto flex max-w-5xl flex-col items-center overflow-hidden px-4 py-16 text-center sm:py-24">
      <div
        className="pointer-events-none absolute -left-32 top-20 h-72 w-72 rounded-full bg-primary/10 blur-3xl animate-float"
        aria-hidden
      />
      <div
        className="pointer-events-none absolute -right-24 bottom-32 h-64 w-64 rounded-full bg-accent/15 blur-3xl animate-float"
        style={{ animationDelay: "1.5s" }}
        aria-hidden
      />

      <div className="animate-fade-in inline-flex items-center gap-2 rounded-full border border-white/70 bg-white/60 px-4 py-2 text-sm font-medium text-muted-foreground shadow-sm backdrop-blur-sm">
        <Sparkles className="h-4 w-4 text-accent" />
        <span>Plateforme de mentorat IA pour étudiants en informatique</span>
      </div>

      <h1 className="animate-slide-up stagger-1 mt-8 text-balance text-4xl font-extrabold tracking-tight opacity-0 sm:text-5xl md:text-6xl">
        Devenez le développeur que vous voulez être avec{" "}
        <span className="bg-gradient-to-r from-primary via-primary to-accent bg-clip-text text-transparent">
          {APP_NAME}
        </span>
      </h1>

      <p className="animate-slide-up stagger-2 mt-6 max-w-2xl text-pretty text-lg leading-relaxed text-muted-foreground opacity-0">
        Analysez votre profil, détectez vos lacunes, obtenez une roadmap personnalisée et
        échangez avec un mentor IA tout au long de votre parcours.
      </p>

      <div className="animate-slide-up stagger-3 mt-10 flex flex-wrap items-center justify-center gap-4 opacity-0">
        <Button asChild size="lg" className="btn-glow rounded-2xl px-8 text-base shadow-lg shadow-primary/20">
          <Link href="/register">
            Commencer gratuitement <ArrowRight className="h-4 w-4" />
          </Link>
        </Button>
        <Button asChild size="lg" variant="outline" className="rounded-2xl border-white/80 bg-white/50 px-8 backdrop-blur-sm">
          <Link href="/login">Se connecter</Link>
        </Button>
      </div>

      <div className="mt-24 grid w-full gap-6 sm:grid-cols-3">
        {FEATURES.map(({ icon: Icon, title, description }, i) => {
          const stagger = ["stagger-4", "stagger-5", "stagger-6"][i];
          return (
            <div
              key={title}
              className={`glass-card-interactive animate-slide-up ${stagger} p-6 text-left opacity-0`}
            >
            <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-primary/15 to-accent/10 text-primary shadow-sm">
              <Icon className="h-6 w-6" />
            </div>
            <h3 className="text-lg font-bold text-[hsl(var(--navy))]">{title}</h3>
            <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{description}</p>
          </div>
          );
        })}
      </div>
    </main>
  );
}
