"use client";

import * as React from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  BrainCircuit,
  CheckCircle2,
  Circle,
  Cloud,
  Database,
  ExternalLink,
  FolderKanban,
  Layers,
  Loader2,
  Rocket,
  Shield,
  Smartphone,
  Sparkles,
  Target,
  TestTube2,
  Workflow,
  Zap,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { Motion } from "@/components/ui/motion";
import { levelLabel } from "@/services/analysis";
import {
  fetchProjectCompletions,
  fetchProjectRecommendations,
  markProjectComplete,
  unmarkProjectComplete,
} from "@/services/projects";
import { useAppReady } from "@/lib/use-app-ready";
import { isApiError } from "@/services/api";
import type { RecommendedProject } from "@/types";
import { cn } from "@/lib/utils";

const DIFFICULTY_LABELS: Record<string, string> = {
  debutant: "Débutant",
  intermediaire: "Intermédiaire",
  avance: "Avancé",
};

type TrackStyle = { label: string; icon: typeof Rocket; accent: string };

const DEFAULT_TRACK_STYLE: TrackStyle = {
  label: "Développement",
  icon: Rocket,
  accent: "from-blue-500/15 to-indigo-500/10",
};

const TRACK_STYLES: Record<string, TrackStyle> = {
  ai: { label: "IA / GenAI", icon: BrainCircuit, accent: "from-violet-500/20 to-fuchsia-500/10" },
  ml: { label: "ML / MLOps", icon: BrainCircuit, accent: "from-indigo-500/15 to-violet-500/10" },
  data: { label: "Data", icon: Database, accent: "from-emerald-500/15 to-teal-500/10" },
  backend: { label: "Backend", icon: Layers, accent: "from-slate-500/15 to-blue-500/10" },
  frontend: { label: "Frontend", icon: Rocket, accent: "from-sky-500/15 to-blue-500/10" },
  fullstack: { label: "Fullstack", icon: Rocket, accent: "from-blue-500/15 to-indigo-500/10" },
  mobile: { label: "Mobile", icon: Smartphone, accent: "from-cyan-500/15 to-blue-500/10" },
  devops: { label: "DevOps / SRE", icon: Workflow, accent: "from-orange-500/15 to-amber-500/10" },
  cloud: { label: "Cloud", icon: Cloud, accent: "from-amber-500/15 to-yellow-500/10" },
  security: { label: "Cybersécurité", icon: Shield, accent: "from-red-500/15 to-rose-500/10" },
  qa: { label: "QA / Tests", icon: TestTube2, accent: "from-lime-500/15 to-green-500/10" },
  product: { label: "Product", icon: Target, accent: "from-pink-500/15 to-rose-500/10" },
  design: { label: "UX / UI", icon: Target, accent: "from-violet-500/15 to-purple-500/10" },
  dev: DEFAULT_TRACK_STYLE,
};

function ProjectCard({
  project,
  index,
  completed,
  onToggle,
  toggling,
}: {
  project: RecommendedProject;
  index: number;
  completed: boolean;
  onToggle: () => void;
  toggling: boolean;
}) {
  const track = TRACK_STYLES[project.track] ?? DEFAULT_TRACK_STYLE;
  const TrackIcon = track.icon;
  const difficulty = DIFFICULTY_LABELS[project.difficulty] ?? project.difficulty;
  const dataSources = project.data_sources ?? [];
  const stack = project.stack ?? [];
  const skillsPracticed = project.skills_practiced ?? [];
  const deliverables = project.deliverables ?? [];
  const motionDelay = Math.min(index + 2, 6) as 1 | 2 | 3 | 4 | 5 | 6;

  return (
    <Motion animation="slide-up" delay={motionDelay}>
      <article className="glass-card-interactive overflow-hidden">
        <div className={cn("bg-gradient-to-br px-5 py-4 sm:px-6", track.accent)}>
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div className="flex items-center gap-2">
              <span className="inline-flex items-center gap-1.5 rounded-full bg-white/80 px-3 py-1 text-xs font-semibold text-[hsl(var(--navy))] shadow-sm">
                <TrackIcon className="h-3.5 w-3.5 text-primary" />
                {track.label}
              </span>
              <span className="rounded-full bg-[hsl(var(--navy))]/10 px-3 py-1 text-xs font-medium text-[hsl(var(--navy))]">
                {difficulty}
              </span>
              <span className="rounded-full bg-white/60 px-3 py-1 text-xs text-muted-foreground">
                ~{project.estimated_weeks} sem.
              </span>
            </div>
            <FolderKanban className="hidden h-8 w-8 text-primary/40 sm:block" />
          </div>
          <h3 className="mt-3 text-xl font-extrabold tracking-tight text-[hsl(var(--navy))]">{project.title}</h3>
          <p className="mt-1 text-sm font-medium text-primary">{project.tagline}</p>
        </div>

        <div className="space-y-4 p-5 sm:p-6">
          <p className="text-sm leading-relaxed text-muted-foreground">{project.description}</p>

          {project.impact && (
            <div className="rounded-2xl border border-primary/15 bg-primary/5 p-4">
              <div className="mb-1.5 flex items-center gap-2 text-xs font-bold uppercase tracking-wide text-primary">
                <Zap className="h-3.5 w-3.5" />
                Impact & portfolio
              </div>
              <p className="text-sm leading-relaxed text-[hsl(var(--navy))]">{project.impact}</p>
            </div>
          )}

          {dataSources.length > 0 && (
            <div>
              <p className="mb-2 text-xs font-bold uppercase tracking-wide text-[hsl(var(--navy))]">
                Sources de données
              </p>
              <ul className="space-y-2">
                {dataSources.map((source) => (
                  <li key={source.url}>
                    <a
                      href={source.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="group flex items-start gap-2 rounded-xl border border-border/60 bg-white/70 p-3 transition hover:border-primary/30 hover:bg-primary/5"
                    >
                      <ExternalLink className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
                      <div>
                        <p className="text-sm font-semibold text-[hsl(var(--navy))] group-hover:text-primary">
                          {source.name}
                        </p>
                        {source.note && <p className="mt-0.5 text-xs text-muted-foreground">{source.note}</p>}
                      </div>
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {stack.length > 0 && (
            <div>
              <p className="mb-2 text-xs font-bold uppercase tracking-wide text-[hsl(var(--navy))]">Stack conseillée</p>
              <div className="flex flex-wrap gap-2">
                {stack.map((tech) => (
                  <span
                    key={tech}
                    className="rounded-full bg-[hsl(var(--navy))]/8 px-3 py-1 text-xs font-medium text-[hsl(var(--navy))]"
                  >
                    {tech}
                  </span>
                ))}
              </div>
            </div>
          )}

          {skillsPracticed.length > 0 && (
            <div>
              <p className="mb-2 text-xs font-bold uppercase tracking-wide text-[hsl(var(--navy))]">
                Compétences travaillées
              </p>
              <div className="flex flex-wrap gap-2">
                {skillsPracticed.map((skill) => (
                  <span
                    key={skill}
                    className="rounded-full border border-primary/20 bg-primary/5 px-3 py-1 text-xs font-medium text-primary"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          )}

          {deliverables.length > 0 && (
            <div>
              <p className="mb-2 text-xs font-bold uppercase tracking-wide text-[hsl(var(--navy))]">Livrables attendus</p>
              <ul className="space-y-1.5">
                {deliverables.map((item) => (
                  <li key={item} className="flex items-start gap-2 text-sm text-muted-foreground">
                    <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-primary" />
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          )}

          <Button
            type="button"
            variant={completed ? "secondary" : "default"}
            className="w-full rounded-2xl"
            disabled={toggling}
            onClick={onToggle}
          >
            {toggling ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : completed ? (
              <CheckCircle2 className="mr-2 h-4 w-4 text-green-600" />
            ) : (
              <Circle className="mr-2 h-4 w-4" />
            )}
            {completed ? "Projet réalisé — cliquer pour annuler" : "Marquer comme réalisé"}
          </Button>
          {completed && (
            <p className="text-center text-xs text-muted-foreground">
              Ce projet compte pour votre niveau d&apos;expérience (roadmap et analyse).
            </p>
          )}
        </div>
      </article>
    </Motion>
  );
}

export default function ProjectsPage() {
  const queryClient = useQueryClient();
  const appReady = useAppReady();
  const { data, isLoading, isError, error } = useQuery({
    queryKey: ["projects", "recommendations"],
    queryFn: fetchProjectRecommendations,
    enabled: appReady,
    staleTime: 15 * 60 * 1000,
  });

  const { data: completions = [] } = useQuery({
    queryKey: ["projects", "completions"],
    queryFn: fetchProjectCompletions,
    enabled: appReady,
  });

  const [togglingTitle, setTogglingTitle] = React.useState<string | null>(null);

  const toggleMutation = useMutation({
    mutationFn: async ({ title, done, careerSlug }: { title: string; done: boolean; careerSlug: string }) => {
      setTogglingTitle(title);
      return done ? unmarkProjectComplete(title) : markProjectComplete(title, careerSlug);
    },
    onSuccess: (completed) => {
      queryClient.setQueryData(["projects", "completions"], completed);
      queryClient.invalidateQueries({ queryKey: ["analysis", "me"] });
      queryClient.invalidateQueries({ queryKey: ["projects", "recommendations"] });
      queryClient.invalidateQueries({ queryKey: ["roadmap", "suggestion"] });
    },
    onSettled: () => setTogglingTitle(null),
  });
  const refreshMutation = useMutation({
    mutationFn: fetchProjectRecommendations,
    onSuccess: (result) => {
      queryClient.setQueryData(["projects", "recommendations"], result);
    },
  });

  const loading = isLoading || refreshMutation.isPending;

  return (
    <div className="mx-auto max-w-4xl">
      <Motion animation="slide-up" delay={1} className="mb-6 flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-[hsl(var(--navy))]">Projets recommandés</h1>
          <p className="text-muted-foreground">
            Projets sur mesure pour votre métier — RAG et pgvector pour l&apos;IA, pipelines pour la data,
            infra pour le DevOps, etc.
          </p>
        </div>
        <Button
          onClick={() => refreshMutation.mutate()}
          disabled={loading || !data}
          className="btn-glow rounded-2xl"
        >
          {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Sparkles className="mr-2 h-4 w-4" />}
          {data ? "Régénérer" : "Chargement…"}
        </Button>
      </Motion>

      {isLoading ? (
        <div className="flex flex-col items-center justify-center gap-3 py-16 text-sm text-muted-foreground">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          Génération de projets personnalisés…
        </div>
      ) : isError ? (
        <div className="glass-card p-8 text-center text-sm text-destructive">
          {isApiError(error) ? error.error.message : "Impossible de charger les recommandations."}
        </div>
      ) : !data || data.projects.length === 0 ? (
        <div className="glass-card p-8 text-center text-sm text-muted-foreground">
          Aucun projet recommandé pour le moment. Lancez d&apos;abord une analyse de compétences.
        </div>
      ) : (
        <>
          <Motion animation="scale-in" delay={2}>
            <div className="glass-card mb-6 flex flex-wrap items-center gap-x-4 gap-y-2 p-4 text-sm">
              <span>
                Métier : <strong>{data.career_name}</strong>
              </span>
              <span className="hidden text-muted-foreground sm:inline">·</span>
              <span>
                Niveau d&apos;expérience : <strong>{levelLabel(data.level)}</strong>
              </span>
              <span className="hidden text-muted-foreground sm:inline">·</span>
              <span>
                Préparation métier : <strong>{data.score}/100</strong>
              </span>
            </div>
          </Motion>

          {refreshMutation.isError && (
            <p className="mb-4 text-sm text-destructive">
              {isApiError(refreshMutation.error)
                ? refreshMutation.error.error.message
                : "Échec de la régénération."}
            </p>
          )}

          <div className="grid gap-6">
            {data.projects.map((project, i) => (
              <ProjectCard
                key={`${project.title}-${i}`}
                project={project}
                index={i}
                completed={completions.includes(project.title)}
                toggling={togglingTitle === project.title}
                onToggle={() =>
                  toggleMutation.mutate({
                    title: project.title,
                    done: completions.includes(project.title),
                    careerSlug: data.career_slug,
                  })
                }
              />
            ))}
          </div>
        </>
      )}
    </div>
  );
}
