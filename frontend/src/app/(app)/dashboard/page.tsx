"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import {
  BarChart3,
  BrainCircuit,
  CheckCircle2,
  Circle,
  FileText,
  Github,
  Loader2,
  Map,
  Target,
} from "lucide-react";

import { Motion } from "@/components/ui/motion";
import { fetchLatestAnalysis, levelLabel } from "@/services/analysis";
import { fetchMyCV } from "@/services/cv";
import { fetchGitHubAnalysis } from "@/services/github";
import { fetchActiveRoadmap } from "@/services/roadmap";
import { useAuthStore } from "@/store/auth-store";
import { computeProfileProgress, fetchMyProfile } from "@/services/profile";

const STEPS = [
  { id: "profile", label: "Compléter le profil", href: "/profile", check: (p: boolean, g: boolean) => p },
  { id: "cv", label: "Téléverser le CV", href: "/cv", check: (_p: boolean, _g: boolean, cv: boolean) => cv },
  { id: "github", label: "Analyser GitHub", href: "/github", check: (_p: boolean, g: boolean) => g },
  { id: "analysis", label: "Lancer le skill gap", href: "/analysis", check: (_p: boolean, _g: boolean, _cv: boolean, a: boolean) => a },
  { id: "roadmap", label: "Générer la roadmap", href: "/roadmap", check: (_p: boolean, _g: boolean, _cv: boolean, _a: boolean, r: boolean) => r },
  { id: "mentor", label: "Parler au mentor IA", href: "/mentor", check: () => false },
  { id: "projects", label: "Voir les projets", href: "/projects", check: (_p: boolean, _g: boolean, _cv: boolean, a: boolean) => a },
  { id: "quiz", label: "Passer l'évaluation", href: "/quiz", check: () => false },
];

export default function DashboardPage() {
  const user = useAuthStore((s) => s.user);
  const { data: profile, isLoading: profileLoading } = useQuery({
    queryKey: ["profile", "me"],
    queryFn: fetchMyProfile,
  });
  const { data: analysis } = useQuery({ queryKey: ["analysis", "me"], queryFn: fetchLatestAnalysis });
  const { data: cv } = useQuery({ queryKey: ["cv", "me"], queryFn: fetchMyCV });
  const { data: github } = useQuery({ queryKey: ["github", "me"], queryFn: fetchGitHubAnalysis });
  const { data: roadmap } = useQuery({ queryKey: ["roadmap", "me"], queryFn: fetchActiveRoadmap });

  const progress = computeProfileProgress(profile ?? null);
  const hasProfile = progress > 20;
  const hasCv = Boolean(cv?.status === "parsed");
  const hasGithub = Boolean(github);
  const hasAnalysis = Boolean(analysis);
  const hasRoadmap = Boolean(roadmap);

  const completed = STEPS.filter((s) => {
    if (s.id === "profile") return hasProfile;
    if (s.id === "cv") return hasCv;
    if (s.id === "github") return hasGithub;
    if (s.id === "analysis") return hasAnalysis;
    if (s.id === "roadmap") return hasRoadmap;
    if (s.id === "projects") return hasAnalysis;
    return false;
  }).length;

  const firstName = user?.firstname ?? "étudiant";

  if (profileLoading) {
    return (
      <div className="flex min-h-[40vh] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <Motion animation="slide-up" delay={1}>
        <div className="flex flex-wrap items-end justify-between gap-4">
          <div>
            <h1 className="text-3xl font-extrabold tracking-tight text-[hsl(var(--navy))] md:text-4xl">
              Bienvenue, {firstName}
            </h1>
            <p className="mt-2 text-muted-foreground">Votre parcours mentor IA — {completed}/{STEPS.length} étapes</p>
          </div>
          {analysis && (
            <div className="glass-card px-5 py-3 text-center">
              <p className="text-xs text-muted-foreground">Score compétences</p>
              <p className="text-2xl font-extrabold text-primary">{analysis.score}/100</p>
              <p className="text-xs">{levelLabel(analysis.level)}</p>
            </div>
          )}
        </div>
      </Motion>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <QuickCard href="/cv" icon={FileText} label="CV" done={hasCv} />
        <QuickCard href="/github" icon={Github} label="GitHub" done={hasGithub} />
        <QuickCard href="/analysis" icon={BarChart3} label="Skill gap" done={hasAnalysis} />
        <QuickCard href="/roadmap" icon={Map} label="Roadmap" done={hasRoadmap} />
      </div>

      <div className="grid gap-6 lg:grid-cols-12">
        <Motion animation="slide-up" delay={2} className="lg:col-span-5 space-y-4">
          <div className="glass-card-interactive p-6">
            <h2 className="mb-2 text-xl font-bold">{user?.firstname} {user?.lastname}</h2>
            <p className="text-sm text-muted-foreground">{profile?.career_goal ?? "Objectif à définir"}</p>
            <div className="mt-4">
              <div className="mb-1 flex justify-between text-sm">
                <span>Profil</span>
                <span className="font-semibold">{progress}%</span>
              </div>
              <div className="h-2 overflow-hidden rounded-full bg-secondary">
                <div className="progress-bar-fill h-full rounded-full bg-primary" style={{ width: `${progress}%` }} />
              </div>
            </div>
            <Link href="/profile" className="btn-glow mt-4 inline-flex rounded-2xl bg-primary px-4 py-2 text-sm font-semibold text-white">
              Modifier le profil
            </Link>
          </div>

          <div className="glass-card-interactive group p-6">
            <div className="mb-3 flex items-center gap-2">
              <BrainCircuit className="h-5 w-5 text-primary" />
              <h3 className="font-semibold">Mentor IA</h3>
            </div>
            <p className="mb-4 text-sm text-muted-foreground">
              Contexte enrichi : profil, CV, GitHub, score et roadmap.
            </p>
            <Link href="/mentor" className="inline-flex rounded-2xl bg-[hsl(var(--navy))] px-4 py-2 text-sm font-semibold text-white">
              Ouvrir le chat
            </Link>
          </div>
        </Motion>

        <Motion animation="slide-up" delay={3} className="lg:col-span-7">
          <div className="glass-card-dark p-6">
            <div className="mb-4 flex items-center justify-between">
              <h3 className="font-semibold">Parcours MVP</h3>
              <span className="rounded-full bg-white/10 px-2 py-0.5 text-xs">{completed}/{STEPS.length}</span>
            </div>
            <div className="mb-4 h-2 overflow-hidden rounded-full bg-white/10">
              <div
                className="progress-bar-fill h-full rounded-full bg-gradient-to-r from-accent to-primary"
                style={{ width: `${(completed / STEPS.length) * 100}%` }}
              />
            </div>
            <ul className="space-y-1">
              {STEPS.map((step) => {
                let done = false;
                if (step.id === "profile") done = hasProfile;
                else if (step.id === "cv") done = hasCv;
                else if (step.id === "github") done = hasGithub;
                else if (step.id === "analysis" || step.id === "projects") done = hasAnalysis;
                else if (step.id === "roadmap") done = hasRoadmap;
                return (
                  <li key={step.id}>
                    <Link
                      href={step.href as "/dashboard"}
                      className="flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm transition-colors hover:bg-white/10"
                    >
                      {done ? (
                        <CheckCircle2 className="h-4 w-4 shrink-0 text-accent" />
                      ) : (
                        <Circle className="h-4 w-4 shrink-0 text-white/40" />
                      )}
                      <span className={done ? "text-white/60 line-through" : ""}>{step.label}</span>
                    </Link>
                  </li>
                );
              })}
            </ul>
          </div>
        </Motion>
      </div>
    </div>
  );
}

function QuickCard({
  href,
  icon: Icon,
  label,
  done,
}: {
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  done: boolean;
}) {
  return (
    <Link
      href={href as "/dashboard"}
      className="glass-card-interactive flex items-center gap-3 p-4 transition-transform hover:-translate-y-0.5"
    >
      <span className={`flex h-10 w-10 items-center justify-center rounded-xl ${done ? "bg-green-500/15 text-green-600" : "bg-primary/10 text-primary"}`}>
        <Icon className="h-5 w-5" />
      </span>
      <div>
        <p className="font-semibold">{label}</p>
        <p className="text-xs text-muted-foreground">{done ? "Complété" : "À faire"}</p>
      </div>
      {done && <Target className="ml-auto h-4 w-4 text-green-600" />}
    </Link>
  );
}
