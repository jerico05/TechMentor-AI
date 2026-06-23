"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { AlertCircle, Github, Loader2, RefreshCw } from "lucide-react";
import * as React from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useAppReady } from "@/lib/use-app-ready";
import { analyzeGitHub, fetchGitHubAnalysis } from "@/services/github";
import { fetchMyProfile } from "@/services/profile";
import { isApiError } from "@/services/api";

function githubStatusLabel(status: string): { label: string; className: string } {
  switch (status) {
    case "completed":
      return { label: "Analyse terminée", className: "text-green-600" };
    case "processing":
      return { label: "Analyse en cours…", className: "text-amber-600" };
    case "failed":
      return { label: "Échec de l'analyse", className: "text-destructive" };
    default:
      return { label: status, className: "text-muted-foreground" };
  }
}

export function GitHubSettingsPanel() {
  const queryClient = useQueryClient();
  const appReady = useAppReady();
  const { data: profile } = useQuery({
    queryKey: ["profile", "me"],
    queryFn: fetchMyProfile,
    enabled: appReady,
  });
  const { data: analysis, isLoading } = useQuery({
    queryKey: ["github", "me"],
    queryFn: fetchGitHubAnalysis,
    enabled: appReady,
    refetchInterval: (q) => (q.state.data?.status === "processing" ? 2000 : false),
  });
  const [url, setUrl] = React.useState("");

  React.useEffect(() => {
    if (profile?.github_url) setUrl(profile.github_url);
  }, [profile?.github_url]);

  const mutation = useMutation({
    mutationFn: () => analyzeGitHub(url || undefined),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["github", "me"] }),
  });

  const statusInfo = analysis ? githubStatusLabel(analysis.status) : null;
  const isProcessing = analysis?.status === "processing" || mutation.isPending;

  return (
    <div className="space-y-6">
      <div className="glass-card space-y-4 p-6">
        <p className="text-sm text-muted-foreground">
          Analysez vos dépôts et langages pour enrichir votre profil mentor.
        </p>
        <Input
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://github.com/votre-compte"
          className="input-modern"
        />
        <Button onClick={() => mutation.mutate()} disabled={isProcessing || !url} className="rounded-2xl">
          {isProcessing ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Github className="mr-2 h-4 w-4" />}
          {isProcessing ? "Analyse en cours…" : "Analyser mon GitHub"}
        </Button>
        {mutation.isError && (
          <p className="text-sm text-destructive">
            {isApiError(mutation.error) ? mutation.error.error.message : "Analyse impossible."}
          </p>
        )}
      </div>

      {isLoading ? (
        <div className="flex justify-center py-6">
          <Loader2 className="h-6 w-6 animate-spin" />
        </div>
      ) : analysis ? (
        <div className="glass-card space-y-4 p-6">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <p className={`text-sm font-medium ${statusInfo?.className}`}>{statusInfo?.label}</p>
            {analysis.status === "processing" && (
              <Loader2 className="h-4 w-4 animate-spin text-amber-600" />
            )}
          </div>

          {analysis.status === "failed" && (
            <div className="flex items-start gap-2 rounded-xl border border-destructive/30 bg-destructive/10 p-4 text-sm text-destructive">
              <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
              <div>
                <p className="font-medium">Impossible d&apos;analyser ce compte GitHub.</p>
                <p className="mt-1 text-destructive/80">
                  Vérifiez l&apos;URL, que le profil est public, et réessayez. En cas de limite API GitHub, attendez quelques minutes.
                </p>
              </div>
            </div>
          )}

          {analysis.status === "processing" && (
            <div className="space-y-2">
              <p className="text-sm text-amber-600">Récupération des dépôts et langages…</p>
              <p className="text-xs text-muted-foreground">
                Cela prend en général quelques secondes. Si le statut ne change pas, rechargez la page.
              </p>
            </div>
          )}

          {analysis.status === "completed" && (
            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <p className="text-sm text-muted-foreground">Utilisateur</p>
                <p className="text-xl font-bold">@{analysis.username}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Dépôts</p>
                <p className="text-xl font-bold">{analysis.repo_count}</p>
              </div>
              <div className="sm:col-span-2">
                <p className="mb-2 text-sm font-medium">Langages</p>
                <div className="flex flex-wrap gap-2">
                  {Object.keys(analysis.languages ?? {}).length > 0 ? (
                    Object.entries(analysis.languages ?? {}).map(([lang, count]) => (
                      <span key={lang} className="rounded-full bg-primary/10 px-3 py-1 text-sm font-medium text-primary">
                        {lang} ({count})
                      </span>
                    ))
                  ) : (
                    <span className="text-sm text-muted-foreground">Aucun langage détecté</span>
                  )}
                </div>
              </div>
              {(analysis.technologies?.length ?? 0) > 0 && (
                <div className="sm:col-span-2">
                  <p className="mb-2 text-sm font-medium">Technologies (topics)</p>
                  <div className="flex flex-wrap gap-2">
                    {analysis.technologies!.map((tech) => (
                      <span key={tech} className="rounded-full bg-accent/15 px-3 py-1 text-sm font-medium text-accent-foreground">
                        {tech}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          <Button
            variant="outline"
            size="sm"
            onClick={() => mutation.mutate()}
            disabled={isProcessing}
            className="w-full rounded-xl sm:w-auto"
          >
            <RefreshCw className="mr-2 h-4 w-4" /> Actualiser
          </Button>
        </div>
      ) : null}
    </div>
  );
}
