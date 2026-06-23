"use client";

import Link from "next/link";
import * as React from "react";
import { useQuery } from "@tanstack/react-query";
import {
  BarChart3,
  BrainCircuit,
  CheckCircle2,
  ChevronRight,
  Circle,
  FileText,
  Github,
  Map,
  MessageSquare,
} from "lucide-react";

import { ProgressRing } from "@/components/crextio/progress-ring";
import { Motion } from "@/components/ui/motion";
import { useAppReady } from "@/lib/use-app-ready";
import { useMounted } from "@/lib/use-mounted";
import { fetchLatestAnalysis } from "@/services/analysis";
import { fetchMyCV } from "@/services/cv";
import { fetchGitHubAnalysis } from "@/services/github";
import { fetchSessions } from "@/services/mentor";
import { fetchQuizHistory } from "@/services/quiz";
import { fetchActiveRoadmap } from "@/services/roadmap";
import { useAuthStore } from "@/store/auth-store";
import { computeProfileProgress, fetchMyProfile } from "@/services/profile";

const STEPS = [
  { id: "profile", label: "Compléter le profil", href: "/settings#settings-profile" },
  { id: "cv", label: "Téléverser le CV", href: "/settings#settings-cv" },
  { id: "github", label: "Analyser GitHub", href: "/settings#settings-github" },
  { id: "analysis", label: "Lancer le skill gap", href: "/analysis" },
  { id: "roadmap", label: "Générer la roadmap", href: "/roadmap" },
  { id: "mentor", label: "Parler au mentor IA", href: "/mentor" },
  { id: "projects", label: "Voir les projets", href: "/projects" },
  { id: "quiz", label: "Passer l'évaluation", href: "/quiz" },
] as const;

const QUICK_LINKS = [
  { label: "Paramètres", href: "/settings" },
  { label: "Analyse CV", href: "/settings#settings-cv" },
  { label: "GitHub", href: "/settings#settings-github" },
  { label: "Roadmap", href: "/roadmap" },
  { label: "Mentor IA", href: "/mentor" },
];

const PROGRESS_METRICS = [
  { key: "cv", label: "CV", href: "/settings#settings-cv" },
  { key: "github", label: "GitHub", href: "/settings#settings-github" },
  { key: "analysis", label: "Analyse", href: "/analysis" },
  { key: "roadmap", label: "Roadmap", href: "/roadmap" },
] as const;

const WEEK_DAYS = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"];

export default function DashboardPage() {
  const mounted = useMounted();
  const user = useAuthStore((s) => s.user);
  const appReady = useAppReady();
  const queryEnabled = { enabled: appReady };

  const { data: profile, isLoading: profileLoading } = useQuery({
    queryKey: ["profile", "me"],
    queryFn: fetchMyProfile,
    ...queryEnabled,
  });
  const { data: analysis } = useQuery({
    queryKey: ["analysis", "me"],
    queryFn: fetchLatestAnalysis,
    ...queryEnabled,
  });
  const { data: cv } = useQuery({
    queryKey: ["cv", "me"],
    queryFn: fetchMyCV,
    ...queryEnabled,
  });
  const { data: github } = useQuery({
    queryKey: ["github", "me"],
    queryFn: fetchGitHubAnalysis,
    ...queryEnabled,
  });
  const { data: roadmap } = useQuery({
    queryKey: ["roadmap", "me"],
    queryFn: fetchActiveRoadmap,
    ...queryEnabled,
  });
  const { data: sessions } = useQuery({
    queryKey: ["mentor", "sessions"],
    queryFn: fetchSessions,
    ...queryEnabled,
  });
  const { data: quizHistory } = useQuery({
    queryKey: ["quiz", "history"],
    queryFn: fetchQuizHistory,
    ...queryEnabled,
  });

  const progress = computeProfileProgress(profile ?? null);
  const hasProfile = progress > 20;
  const hasCv = cv?.status === "parsed";
  const hasGithub = github?.status === "completed";
  const hasAnalysis = Boolean(analysis);
  const hasRoadmap = Boolean(roadmap);
  const hasMentor = Boolean(sessions && sessions.length > 0);
  const hasQuiz = Boolean(quizHistory && quizHistory.length > 0);

  function isStepDone(stepId: (typeof STEPS)[number]["id"]): boolean {
    switch (stepId) {
      case "profile":
        return hasProfile;
      case "cv":
        return hasCv;
      case "github":
        return hasGithub;
      case "analysis":
      case "projects":
        return hasAnalysis;
      case "roadmap":
        return hasRoadmap;
      case "mentor":
        return hasMentor;
      case "quiz":
        return hasQuiz;
      default:
        return false;
    }
  }

  const completed = STEPS.filter((s) => isStepDone(s.id)).length;
  const firstName = user?.firstname ?? "étudiant";
  const overallProgress = Math.round((completed / STEPS.length) * 100);

  const metricDone: Record<string, boolean> = {
    cv: hasCv,
    github: hasGithub,
    analysis: hasAnalysis,
    roadmap: hasRoadmap,
  };

  if (!mounted || profileLoading) {
    return <DashboardSkeleton firstName={user?.firstname ?? "étudiant"} />;
  }

  return (
    <div className="space-y-8">
      {/* En-tête Crextio : titre + stat pills */}
      <Motion animation="slide-up">
        <div className="flex flex-wrap items-center gap-3 md:gap-4">
          <h1 className="text-3xl font-light tracking-tight text-muted-foreground md:text-4xl lg:text-5xl">
            Bienvenue,{" "}
            <span className="font-extrabold text-[hsl(var(--navy))]">{firstName}</span>
          </h1>
          <div className="flex flex-wrap items-center gap-2">
            <span className="stat-pill-muted">
              Profil <strong className="text-foreground">{progress}%</strong>
            </span>
            {analysis && (
              <span className="stat-pill-active">
                Score <strong>{analysis.score}/100</strong>
              </span>
            )}
            <span className="stat-pill-accent">
              Parcours <strong>{overallProgress}%</strong>
            </span>
            {hasQuiz && (
              <span className="stat-pill-muted">
                Quiz <strong className="text-foreground">{quizHistory?.length}</strong>
              </span>
            )}
          </div>
        </div>
      </Motion>

      {/* Grille principale */}
      <div className="grid gap-6 lg:grid-cols-12">
        {/* Colonne gauche - profil + menu */}
        <Motion animation="slide-up" className="space-y-4 lg:col-span-3">
          <div className="glass-card overflow-hidden">
            <div className="relative h-44 bg-gradient-to-br from-primary/20 via-secondary to-primary/10">
              <div className="absolute inset-x-0 bottom-0 flex h-24 items-end bg-gradient-to-t from-white via-white/90 to-transparent px-6 pb-4">
                <div className="flex w-full items-end justify-between gap-2">
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-lg font-bold text-[hsl(var(--navy))]">
                      {user?.firstname} {user?.lastname}
                    </p>
                    <p className="truncate text-sm text-muted-foreground">
                      {profile?.career_goal ?? "Objectif à définir"}
                    </p>
                  </div>
                  <span className="shrink-0 rounded-full bg-[hsl(var(--navy))] px-3 py-1 text-xs font-semibold text-white">
                    {progress}%
                  </span>
                </div>
              </div>
              <div className="absolute left-6 top-6 flex h-16 w-16 items-center justify-center rounded-2xl bg-white text-xl font-bold text-[hsl(var(--navy))] shadow-lg">
                {user?.firstname?.[0]}
                {user?.lastname?.[0]}
              </div>
            </div>
            <div className="p-4">
              <Link href="/settings" className="btn-navy w-full text-center">
                Modifier le profil
              </Link>
            </div>
          </div>

          <div className="glass-card p-2">
            {QUICK_LINKS.map((link) => (
              <Link key={link.href} href={link.href as "/dashboard"} className="crextio-menu-item">
                {link.label}
                <ChevronRight className="h-4 w-4 text-muted-foreground" />
              </Link>
            ))}
          </div>
        </Motion>

        {/* Colonne centrale - progression + time tracker */}
        <Motion animation="slide-up" className="space-y-4 lg:col-span-5">
          <div className="glass-card p-6">
            <div className="mb-6 flex items-center justify-between">
              <h2 className="text-lg font-bold text-[hsl(var(--navy))]">Progression</h2>
              <span className="text-sm text-muted-foreground">{completed}/{STEPS.length} étapes</span>
            </div>
            <div className="mb-6 flex items-end justify-between gap-3 px-1">
              {PROGRESS_METRICS.map((m, i) => {
                const done = metricDone[m.key];
                const maxHeights = [72, 96, 58, 110];
                const barHeight = done ? maxHeights[i]! : Math.round(maxHeights[i]! * 0.35);
                return (
                  <Link
                    key={m.key}
                    href={m.href as "/dashboard"}
                    className="group flex flex-1 flex-col items-center gap-2"
                  >
                    <div className="relative flex h-28 w-full max-w-14 items-end justify-center">
                      <div
                        className="absolute inset-x-0 bottom-0 top-0 rounded-2xl bg-secondary/50"
                        aria-hidden
                      />
                      <div
                        className={`relative w-full max-w-[2.75rem] rounded-t-2xl transition-all duration-700 ease-out group-hover:opacity-90 ${
                          done ? "bg-primary shadow-sm shadow-primary/25" : "bg-primary/20"
                        }`}
                        style={{ height: barHeight }}
                      />
                    </div>
                    <span
                      className={`text-xs font-medium ${done ? "text-[hsl(var(--navy))]" : "text-muted-foreground"}`}
                    >
                      {m.label}
                    </span>
                    {done ? (
                      <CheckCircle2 className="h-3.5 w-3.5 text-primary" aria-hidden />
                    ) : (
                      <Circle className="h-3.5 w-3.5 text-muted-foreground/40" aria-hidden />
                    )}
                  </Link>
                );
              })}
            </div>
            <div className="mt-4">
              <div className="mb-1 flex justify-between text-sm">
                <span className="text-muted-foreground">Profil complété</span>
                <span className="font-semibold text-[hsl(var(--navy))]">{progress}%</span>
              </div>
              <div className="progress-bar-track h-2.5">
                <div className="progress-bar-fill h-full" style={{ width: `${progress}%` }} />
              </div>
            </div>
          </div>

          <div className="glass-card flex flex-col items-center p-6 sm:flex-row sm:justify-around sm:gap-6">
            <div className="text-center sm:text-left">
              <h2 className="text-lg font-bold text-[hsl(var(--navy))]">Time tracker</h2>
              <p className="mt-1 text-sm text-muted-foreground">Avancement de votre parcours</p>
              <Link href="/mentor" className="btn-primary-pill mt-4 inline-flex gap-2">
                <BrainCircuit className="h-4 w-4" />
                {hasMentor ? "Continuer" : "Démarrer"}
              </Link>
            </div>
            <ProgressRing
              value={overallProgress}
              label={`${overallProgress}%`}
              sublabel="complété"
            />
          </div>
        </Motion>

        {/* Colonne droite - tâches sombres */}
        <Motion animation="slide-up" className="lg:col-span-4">
          <div className="glass-card-dark flex h-full min-h-[320px] flex-col p-6">
            <div className="mb-4 flex items-center justify-between">
              <h3 className="font-semibold">Votre parcours</h3>
              <span className="rounded-full bg-white/10 px-3 py-1 text-xs font-medium">
                {completed}/{STEPS.length}
              </span>
            </div>
            <div className="mb-4 h-2 overflow-hidden rounded-full bg-white/10">
              <div
                className="h-full rounded-full bg-primary transition-all duration-700"
                style={{ width: `${overallProgress}%` }}
              />
            </div>
            <ul className="flex-1 space-y-0.5 overflow-y-auto scrollbar-thin">
              {STEPS.map((step) => {
                const done = isStepDone(step.id);
                return (
                  <li key={step.id}>
                    <Link
                      href={step.href}
                      className="flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm transition-colors hover:bg-white/10"
                    >
                      {done ? (
                        <CheckCircle2 className="h-4 w-4 shrink-0 text-primary" />
                      ) : (
                        <Circle className="h-4 w-4 shrink-0 text-white/30" />
                      )}
                      <span className={done ? "text-white/50 line-through" : ""}>{step.label}</span>
                    </Link>
                  </li>
                );
              })}
            </ul>
          </div>
        </Motion>
      </div>

      {/* Calendrier / sessions */}
      <Motion animation="slide-up">
        <div className="glass-card p-6">
          <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
            <h2 className="text-lg font-bold text-[hsl(var(--navy))]">Cette semaine</h2>
            <Link href="/mentor" className="text-sm font-medium text-primary hover:underline">
              Voir le mentor →
            </Link>
          </div>
          <div className="-mx-1 overflow-x-auto px-1 pb-1 [scrollbar-width:thin] sm:mx-0 sm:overflow-visible sm:px-0 sm:pb-0">
            <div className="grid min-w-[280px] grid-cols-7 gap-1 sm:min-w-0 sm:gap-2">
            {WEEK_DAYS.map((day, i) => {
              const isToday = i === new Date().getDay() - 1 || (new Date().getDay() === 0 && i === 6);
              const hasSession = hasMentor && i < (sessions?.length ?? 0);
              return (
                <div
                  key={day}
                  className={`rounded-xl p-2 text-center transition-colors sm:rounded-2xl sm:p-3 ${
                    isToday ? "bg-[hsl(var(--navy))] text-white" : "bg-secondary/50"
                  }`}
                >
                  <p className={`text-[10px] font-medium sm:text-xs ${isToday ? "text-white/70" : "text-muted-foreground"}`}>
                    {day}
                  </p>
                  <p className={`mt-0.5 text-sm font-bold sm:mt-1 sm:text-lg ${isToday ? "" : "text-[hsl(var(--navy))]"}`}>
                    {new Date().getDate() - new Date().getDay() + i + 1}
                  </p>
                  {hasSession && (
                    <>
                      <span
                        className={`mx-auto mt-1.5 block h-1.5 w-1.5 rounded-full sm:hidden ${
                          isToday ? "bg-white/80" : "bg-primary"
                        }`}
                        aria-label="Session mentor"
                      />
                      <div
                        className={`mt-1.5 hidden rounded-full px-1.5 py-0.5 text-[10px] font-medium sm:block ${
                          isToday ? "bg-white/20" : "bg-primary/15 text-primary"
                        }`}
                      >
                        Mentor
                      </div>
                    </>
                  )}
                </div>
              );
            })}
            </div>
          </div>

          {sessions && sessions.length > 0 ? (
            <div className="mt-6 flex flex-wrap gap-3">
              {sessions.slice(0, 3).map((s) => (
                <Link
                  key={s.id}
                  href="/mentor"
                  className="inline-flex max-w-full items-center gap-2 rounded-full bg-secondary/70 px-4 py-2 text-sm font-medium text-[hsl(var(--navy))] transition-colors hover:bg-secondary"
                >
                  <MessageSquare className="h-4 w-4 shrink-0 text-primary" />
                  <span className="truncate">{s.title || "Session mentor"}</span>
                </Link>
              ))}
            </div>
          ) : (
            <p className="mt-6 text-sm text-muted-foreground">
              Aucune session mentor cette semaine,{" "}
              <Link href="/mentor" className="font-medium text-primary hover:underline">
                démarrez une conversation
              </Link>
            </p>
          )}
        </div>
      </Motion>

      {/* Raccourcis bas */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <QuickCard href="/settings#settings-cv" icon={FileText} label="CV" done={hasCv} />
        <QuickCard href="/settings#settings-github" icon={Github} label="GitHub" done={hasGithub} />
        <QuickCard href="/analysis" icon={BarChart3} label="Skill gap" done={hasAnalysis} score={analysis?.score} />
        <QuickCard href="/roadmap" icon={Map} label="Roadmap" done={hasRoadmap} />
      </div>
    </div>
  );
}

function DashboardSkeleton({ firstName }: { firstName: string }) {
  return (
    <div className="space-y-8 animate-pulse">
      <div className="flex flex-wrap items-center gap-4">
        <div className="h-10 w-72 rounded-full bg-secondary" />
        <div className="h-8 w-24 rounded-full bg-secondary" />
        <div className="h-8 w-28 rounded-full bg-secondary" />
      </div>
      <div className="grid gap-6 lg:grid-cols-12">
        <div className="glass-card h-80 lg:col-span-3" />
        <div className="space-y-4 lg:col-span-5">
          <div className="glass-card h-52" />
          <div className="glass-card h-44" />
        </div>
        <div className="glass-card-dark h-80 lg:col-span-4" />
      </div>
      <div className="glass-card h-40" />
      <p className="text-center text-sm text-muted-foreground">Chargement du tableau de bord, {firstName}…</p>
    </div>
  );
}

function QuickCard({
  href,
  icon: Icon,
  label,
  done,
  score,
}: {
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  done: boolean;
  score?: number;
}) {
  return (
    <Link href={href as "/dashboard"} className="glass-card-interactive flex items-center gap-4 p-5">
      <span
        className={`flex h-12 w-12 items-center justify-center rounded-2xl ${
          done ? "bg-primary/15 text-primary" : "bg-secondary text-muted-foreground"
        }`}
      >
        <Icon className="h-5 w-5" />
      </span>
      <div className="min-w-0 flex-1">
        <p className="font-semibold text-[hsl(var(--navy))]">{label}</p>
        <p className="text-xs text-muted-foreground">
          {done ? (score != null ? `Score ${score}/100` : "Complété") : "À faire"}
        </p>
      </div>
      {done && (
        <span className="rounded-full bg-primary/15 px-2.5 py-1 text-xs font-semibold text-primary">
          ✓
        </span>
      )}
    </Link>
  );
}
