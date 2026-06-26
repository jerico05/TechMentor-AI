"use client";

import * as React from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  AlertCircle,
  BrainCircuit,
  CheckCircle2,
  Circle,
  Cloud,
  Database,
  ExternalLink,
  FolderKanban,
  Github,
  Layers,
  Loader2,
  Rocket,
  Shield,
  Smartphone,
  Sparkles,
  Target,
  TestTube2,
  Workflow,
  X,
  Zap,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Motion } from "@/components/ui/motion";
import { levelLabel } from "@/services/analysis";
import { invalidateDashboardSummary } from "@/services/dashboard";
import {
  fetchProjectCompletions,
  fetchProjectRecommendations,
  submitProjectProof,
  unmarkProjectComplete,
  type SubmitProjectPayload,
} from "@/services/projects";
import { useAppReady } from "@/lib/use-app-ready";
import { isApiError } from "@/services/api";
import type { ProjectSubmission, RecommendedProject } from "@/types";
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

function ProofModal({
  project,
  careerSlug,
  onClose,
  onApproved,
}: {
  project: RecommendedProject;
  careerSlug: string;
  onClose: () => void;
  onApproved: () => void;
}) {
  const [githubUrl, setGithubUrl] = React.useState("");
  const [description, setDescription] = React.useState("");
  const [result, setResult] = React.useState<ProjectSubmission | null>(null);

  const mutation = useMutation({
    mutationFn: () => {
      const payload: SubmitProjectPayload = {
        project_title: project.title,
        career_slug: careerSlug,
        project_description: project.description,
        skills_practiced: project.skills_practiced ?? [],
        deliverables: project.deliverables ?? [],
        github_url: githubUrl.trim() || null,
        user_description: description.trim() || null,
      };
      return submitProjectProof(payload);
    },
    onSuccess: (data) => {
      setResult(data);
      if (data.status === "approved") {
        onApproved();
      }
    },
  });

  const canSubmit = githubUrl.trim().length > 0 || description.trim().length >= 30;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4 backdrop-blur-sm">
      <div className="relative w-full max-w-lg rounded-3xl bg-white shadow-2xl">
        <button
          onClick={onClose}
          className="absolute right-4 top-4 rounded-full p-1.5 text-muted-foreground hover:bg-secondary"
        >
          <X className="h-4 w-4" />
        </button>

        <div className="border-b border-border/50 px-6 pt-6 pb-4">
          <h2 className="text-lg font-extrabold text-[hsl(var(--navy))]">
            Soumettre la preuve
          </h2>
          <p className="mt-1 text-sm text-muted-foreground">
            <span className="font-medium text-[hsl(var(--navy))]">{project.title}</span> - votre travail sera evalué par l&apos;IA avant validation.
          </p>
        </div>

        {result ? (
          <div className="p-6 space-y-4">
            {result.status === "approved" ? (
              <div className="rounded-2xl border border-green-200 bg-green-50 p-4 flex items-start gap-3">
                <CheckCircle2 className="mt-0.5 h-5 w-5 shrink-0 text-green-600" />
                <div>
                  <p className="font-semibold text-green-800">Projet validé !</p>
                  <p className="mt-1 text-sm text-green-700">{result.feedback}</p>
                  <p className="mt-2 text-xs text-green-600">Score : {result.evaluation_score}/100</p>
                </div>
              </div>
            ) : (
              <div className="rounded-2xl border border-orange-200 bg-orange-50 p-4 flex items-start gap-3">
                <AlertCircle className="mt-0.5 h-5 w-5 shrink-0 text-orange-600" />
                <div>
                  <p className="font-semibold text-orange-800">Preuve insuffisante</p>
                  <p className="mt-1 text-sm text-orange-700">{result.feedback}</p>
                  <p className="mt-2 text-xs text-orange-600">Score : {result.evaluation_score}/100 (minimum requis : 60)</p>
                </div>
              </div>
            )}
            <div className="flex gap-2">
              {result.status === "rejected" && (
                <Button
                  variant="outline"
                  className="flex-1 rounded-2xl"
                  onClick={() => { setResult(null); mutation.reset(); }}
                >
                  Reessayer
                </Button>
              )}
              <Button className="flex-1 rounded-2xl" onClick={onClose}>
                Fermer
              </Button>
            </div>
          </div>
        ) : (
          <div className="p-6 space-y-4">
            <div className="rounded-2xl border border-primary/15 bg-primary/5 p-3 text-sm text-[hsl(var(--navy))]">
              <p className="font-semibold mb-1">Ce qui est évalué</p>
              <ul className="space-y-0.5 text-muted-foreground text-xs">
                {(project.deliverables ?? []).slice(0, 3).map((d) => (
                  <li key={d} className="flex items-start gap-1.5">
                    <span className="mt-1 h-1 w-1 shrink-0 rounded-full bg-primary" />
                    {d}
                  </li>
                ))}
              </ul>
            </div>

            <div className="space-y-1.5">
              <Label htmlFor="proof-github" className="flex items-center gap-1.5">
                <Github className="h-3.5 w-3.5" />
                Lien GitHub du projet
              </Label>
              <Input
                id="proof-github"
                value={githubUrl}
                onChange={(e) => setGithubUrl(e.target.value)}
                placeholder="https://github.com/vous/mon-projet"
                className="input-modern"
              />
              <p className="text-xs text-muted-foreground">Dépôt public recommandé.</p>
            </div>

            <div className="space-y-1.5">
              <Label htmlFor="proof-desc">Description de ce que vous avez réalisé</Label>
              <textarea
                id="proof-desc"
                rows={4}
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Décrivez ce que vous avez construit, les fonctionnalités principales, les difficultés surmontées..."
                className="input-modern w-full resize-y rounded-2xl border border-input bg-background px-3 py-2 text-sm"
              />
              {!githubUrl.trim() && (
                <p className="text-xs text-muted-foreground">
                  Sans lien GitHub, au moins 30 caractères requis.
                </p>
              )}
            </div>

            {mutation.isError && (
              <p className="text-sm text-destructive">
                {isApiError(mutation.error) ? mutation.error.error.message : "Envoi impossible."}
              </p>
            )}

            <div className="flex gap-2 pt-2">
              <Button variant="outline" className="flex-1 rounded-2xl" onClick={onClose} disabled={mutation.isPending}>
                Annuler
              </Button>
              <Button
                className="flex-1 rounded-2xl btn-glow"
                onClick={() => mutation.mutate()}
                disabled={mutation.isPending || !canSubmit}
              >
                {mutation.isPending ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Évaluation en cours…
                  </>
                ) : (
                  "Soumettre pour évaluation"
                )}
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function ProjectCard({
  project,
  index,
  completed,
  careerSlug,
  onToggle,
  toggling,
}: {
  project: RecommendedProject;
  index: number;
  completed: boolean;
  careerSlug: string;
  onToggle: () => void;
  toggling: boolean;
}) {
  const [showModal, setShowModal] = React.useState(false);
  const queryClient = useQueryClient();

  const handleApproved = React.useCallback(() => {
    queryClient.invalidateQueries({ queryKey: ["projects", "completions"] });
    queryClient.invalidateQueries({ queryKey: ["analysis", "me"] });
    queryClient.invalidateQueries({ queryKey: ["roadmap", "suggestion"] });
    invalidateDashboardSummary(queryClient);
    setShowModal(false);
  }, [queryClient]);

  const track = TRACK_STYLES[project.track] ?? DEFAULT_TRACK_STYLE;
  const TrackIcon = track.icon;
  const difficulty = DIFFICULTY_LABELS[project.difficulty] ?? project.difficulty;
  const dataSources = project.data_sources ?? [];
  const stack = project.stack ?? [];
  const skillsPracticed = project.skills_practiced ?? [];
  const deliverables = project.deliverables ?? [];
  const motionDelay = Math.min(index + 2, 6) as 1 | 2 | 3 | 4 | 5 | 6;

  return (
    <>
    {showModal && (
      <ProofModal
        project={project}
        careerSlug={careerSlug}
        onClose={() => setShowModal(false)}
        onApproved={handleApproved}
      />
    )}
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

          {completed ? (
            <div className="space-y-2">
              <div className="flex items-center gap-2 rounded-2xl border border-green-200 bg-green-50 px-4 py-3">
                <CheckCircle2 className="h-4 w-4 shrink-0 text-green-600" />
                <span className="flex-1 text-sm font-medium text-green-800">Projet validé - compte pour votre niveau</span>
                <button
                  onClick={onToggle}
                  disabled={toggling}
                  className="rounded-xl px-2 py-1 text-xs text-muted-foreground hover:bg-green-100"
                >
                  {toggling ? <Loader2 className="h-3 w-3 animate-spin" /> : "Annuler"}
                </button>
              </div>
            </div>
          ) : (
            <Button
              type="button"
              className="w-full rounded-2xl btn-glow"
              disabled={toggling}
              onClick={() => setShowModal(true)}
            >
              <Circle className="mr-2 h-4 w-4" />
              J&apos;ai réalisé ce projet — soumettre la preuve
            </Button>
          )}
        </div>
      </article>
    </Motion>
    </>
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
    mutationFn: async ({ title }: { title: string }) => {
      setTogglingTitle(title);
      return unmarkProjectComplete(title);
    },
    onSuccess: (completed) => {
      queryClient.setQueryData(["projects", "completions"], completed);
      queryClient.invalidateQueries({ queryKey: ["analysis", "me"] });
      queryClient.invalidateQueries({ queryKey: ["projects", "recommendations"] });
      queryClient.invalidateQueries({ queryKey: ["roadmap", "suggestion"] });
      invalidateDashboardSummary(queryClient);
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
                careerSlug={data.career_slug}
                toggling={togglingTitle === project.title}
                onToggle={() =>
                  toggleMutation.mutate({ title: project.title })
                }
              />
            ))}
          </div>
        </>
      )}
    </div>
  );
}
