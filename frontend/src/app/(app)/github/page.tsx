"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Github, Loader2, RefreshCw } from "lucide-react";
import * as React from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Motion } from "@/components/ui/motion";
import { analyzeGitHub, fetchGitHubAnalysis } from "@/services/github";
import { fetchMyProfile } from "@/services/profile";
import { isApiError } from "@/services/api";

export default function GitHubPage() {
  const queryClient = useQueryClient();
  const { data: profile } = useQuery({ queryKey: ["profile", "me"], queryFn: fetchMyProfile });
  const { data: analysis, isLoading } = useQuery({
    queryKey: ["github", "me"],
    queryFn: fetchGitHubAnalysis,
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

  return (
    <div className="mx-auto max-w-2xl">
      <Motion animation="slide-up" delay={1} className="mb-6">
        <h1 className="text-3xl font-extrabold tracking-tight text-[hsl(var(--navy))]">GitHub</h1>
        <p className="text-muted-foreground">Analysez vos dépôts et langages pour enrichir votre profil.</p>
      </Motion>

      <Motion animation="scale-in" delay={2} className="glass-card space-y-4 p-6">
        <Input
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://github.com/votre-compte"
          className="input-modern"
        />
        <Button onClick={() => mutation.mutate()} disabled={mutation.isPending || !url} className="rounded-2xl">
          {mutation.isPending ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Github className="mr-2 h-4 w-4" />}
          Analyser mon GitHub
        </Button>
        {mutation.isError && (
          <p className="text-sm text-destructive">
            {isApiError(mutation.error) ? mutation.error.error.message : "Analyse impossible."}
          </p>
        )}
      </Motion>

      {isLoading ? (
        <div className="mt-6 flex justify-center"><Loader2 className="h-6 w-6 animate-spin" /></div>
      ) : analysis ? (
        <Motion animation="slide-up" delay={3} className="glass-card mt-6 grid gap-4 p-6 sm:grid-cols-2">
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
              {Object.entries(analysis.languages ?? {}).map(([lang, count]) => (
                <span key={lang} className="rounded-full bg-primary/10 px-3 py-1 text-sm font-medium text-primary">
                  {lang} ({count})
                </span>
              ))}
            </div>
          </div>
          <Button variant="outline" size="sm" onClick={() => mutation.mutate()} className="sm:col-span-2 rounded-xl">
            <RefreshCw className="mr-2 h-4 w-4" /> Actualiser
          </Button>
        </Motion>
      ) : null}
    </div>
  );
}
