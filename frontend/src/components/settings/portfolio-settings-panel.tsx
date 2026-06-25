"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  AlertCircle,
  ExternalLink,
  FolderKanban,
  Loader2,
  Plus,
  Save,
  Trash2,
} from "lucide-react";
import * as React from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAppReady } from "@/lib/use-app-ready";
import { levelLabel } from "@/services/analysis";
import {
  addPortfolioProject,
  deletePortfolioProject,
  fetchPortfolioProjects,
  invalidatePortfolioQueries,
  savePortfolioUrl,
} from "@/services/portfolio";
import { isApiError } from "@/services/api";
import type { PortfolioProject } from "@/types";
import { cn } from "@/lib/utils";

function projectStatusClass(status: string): string {
  switch (status) {
    case "completed":
      return "text-green-600";
    case "processing":
      return "text-amber-600";
    case "failed":
      return "text-destructive";
    default:
      return "text-muted-foreground";
  }
}

function ProjectRow({
  project,
  onDelete,
  deleting,
}: {
  project: PortfolioProject;
  onDelete: () => void;
  deleting: boolean;
}) {
  return (
    <li className="rounded-2xl border border-white/70 bg-white/80 p-4 shadow-crextio-sm">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <p className="font-semibold text-[hsl(var(--navy))]">{project.title}</p>
            <span className={cn("text-xs font-medium", projectStatusClass(project.status))}>
              {project.status === "completed"
                ? "Extrait"
                : project.status === "processing"
                  ? "Extraction…"
                  : "Échec"}
            </span>
          </div>
          <a
            href={project.url}
            target="_blank"
            rel="noopener noreferrer"
            className="mt-1 inline-flex items-center gap-1 text-xs text-primary hover:underline"
          >
            <ExternalLink className="h-3 w-3" />
            {project.url}
          </a>
          {project.summary ? (
            <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{project.summary}</p>
          ) : null}
          {(project.stack?.length ?? 0) > 0 ? (
            <div className="mt-2 flex flex-wrap gap-1.5">
              {project.stack!.map((tech) => (
                <span
                  key={tech}
                  className="rounded-full bg-secondary px-2 py-0.5 text-[10px] font-semibold text-[hsl(var(--navy))]"
                >
                  {tech}
                </span>
              ))}
            </div>
          ) : null}
        </div>
        <Button
          type="button"
          variant="ghost"
          size="icon"
          disabled={deleting}
          onClick={onDelete}
          className="shrink-0 text-destructive hover:bg-destructive/10"
          aria-label="Supprimer le projet"
        >
          {deleting ? <Loader2 className="h-4 w-4 animate-spin" /> : <Trash2 className="h-4 w-4" />}
        </Button>
      </div>
    </li>
  );
}

export function PortfolioSettingsPanel() {
  const queryClient = useQueryClient();
  const appReady = useAppReady();
  const { data, isLoading } = useQuery({
    queryKey: ["portfolio", "projects"],
    queryFn: fetchPortfolioProjects,
    enabled: appReady,
  });
  const [projectUrl, setProjectUrl] = React.useState("");
  const [siteUrl, setSiteUrl] = React.useState("");
  const [deletingId, setDeletingId] = React.useState<number | null>(null);

  React.useEffect(() => {
    if (data?.portfolio_url) setSiteUrl(data.portfolio_url);
  }, [data?.portfolio_url]);

  const addMutation = useMutation({
    mutationFn: () => addPortfolioProject(projectUrl),
    onSuccess: () => {
      setProjectUrl("");
      invalidatePortfolioQueries(queryClient);
    },
  });

  const siteMutation = useMutation({
    mutationFn: () => savePortfolioUrl(siteUrl.trim() || null),
    onSuccess: () => invalidatePortfolioQueries(queryClient),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => deletePortfolioProject(id),
    onMutate: (id) => setDeletingId(id),
    onSettled: () => setDeletingId(null),
    onSuccess: () => invalidatePortfolioQueries(queryClient),
  });

  const projects = data?.projects ?? [];
  const completed = data?.total_completed ?? 0;

  return (
    <div className="space-y-6">
      <div className="glass-card space-y-4 p-6">
        <p className="text-sm text-muted-foreground">
          Ajoutez le lien de chaque projet réalisé (GitHub, demo, case study). Chaque lien est analysé
          et compte pour votre niveau d&apos;expérience.
        </p>
        <div className="rounded-2xl bg-secondary/40 px-4 py-3 text-sm">
          <span className="font-semibold text-[hsl(var(--navy))]">{completed}</span>{" "}
          projet{completed !== 1 ? "s" : ""} comptabilisé{completed !== 1 ? "s" : ""}
          {completed > 0 ? (
            <span className="text-muted-foreground">
              {" "}
              · niveau actuel basé sur vos projets ({levelLabel(
                completed >= 8 ? "senior" : completed >= 3 ? "intermediaire" : "entry",
              )})
            </span>
          ) : null}
        </div>
        <div className="space-y-1.5">
          <Label htmlFor="project-url">Lien du projet</Label>
          <Input
            id="project-url"
            value={projectUrl}
            onChange={(e) => setProjectUrl(e.target.value)}
            placeholder="https://github.com/vous/mon-projet ou URL de demo"
            className="input-modern"
          />
        </div>
        <Button
          onClick={() => addMutation.mutate()}
          disabled={addMutation.isPending || !projectUrl.trim()}
          className="rounded-2xl"
        >
          {addMutation.isPending ? (
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          ) : (
            <Plus className="mr-2 h-4 w-4" />
          )}
          Ajouter et analyser le projet
        </Button>
        {addMutation.isError && (
          <p className="text-sm text-destructive">
            {isApiError(addMutation.error) ? addMutation.error.error.message : "Ajout impossible."}
          </p>
        )}
      </div>

      <div className="glass-card space-y-4 p-6">
        <div className="space-y-1.5">
          <Label htmlFor="portfolio-site-url">Site portfolio (optionnel)</Label>
          <Input
            id="portfolio-site-url"
            value={siteUrl}
            onChange={(e) => setSiteUrl(e.target.value)}
            placeholder="https://mon-portfolio.dev"
            className="input-modern"
          />
        </div>
        <Button
          variant="outline"
          onClick={() => siteMutation.mutate()}
          disabled={siteMutation.isPending}
          className="rounded-2xl"
        >
          {siteMutation.isPending ? (
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          ) : (
            <Save className="mr-2 h-4 w-4" />
          )}
          Enregistrer l&apos;URL portfolio
        </Button>
      </div>

      {isLoading ? (
        <div className="flex justify-center py-6">
          <Loader2 className="h-6 w-6 animate-spin" />
        </div>
      ) : projects.length > 0 ? (
        <div className="glass-card space-y-4 p-6">
          <h3 className="flex items-center gap-2 font-semibold text-[hsl(var(--navy))]">
            <FolderKanban className="h-4 w-4 text-primary" />
            Mes projets ({projects.length})
          </h3>
          <ul className="space-y-3">
            {projects.map((project) => (
              <ProjectRow
                key={project.id}
                project={project}
                deleting={deletingId === project.id}
                onDelete={() => deleteMutation.mutate(project.id)}
              />
            ))}
          </ul>
        </div>
      ) : (
        <div className="glass-card flex items-start gap-2 p-6 text-sm text-muted-foreground">
          <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
          Aucun projet enregistré. Ajoutez un lien pour que le mentor et votre niveau s&apos;actualisent.
        </div>
      )}
    </div>
  );
}
