"use client";

import { useQuery } from "@tanstack/react-query";
import { FolderKanban, Loader2 } from "lucide-react";

import { Motion } from "@/components/ui/motion";
import { levelLabel } from "@/services/analysis";
import { fetchProjectRecommendations } from "@/services/projects";

export default function ProjectsPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["projects", "recommendations"],
    queryFn: fetchProjectRecommendations,
  });

  return (
    <div className="mx-auto max-w-3xl">
      <Motion animation="slide-up" delay={1} className="mb-6">
        <h1 className="text-3xl font-extrabold tracking-tight text-[hsl(var(--navy))]">Projets recommandés</h1>
        <p className="text-muted-foreground">Des projets adaptés à votre niveau actuel.</p>
      </Motion>

      {isLoading ? (
        <div className="flex justify-center py-16"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>
      ) : data ? (
        <Motion animation="scale-in" delay={2}>
          <div className="glass-card mb-6 p-4 text-sm">
            Niveau : <strong>{levelLabel(data.level)}</strong> — Score : <strong>{data.score}/100</strong>
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            {data.projects.map((p) => (
              <div key={p.title} className="glass-card-interactive p-5">
                <FolderKanban className="mb-2 h-6 w-6 text-primary" />
                <h3 className="font-bold">{p.title}</h3>
                <p className="mt-2 text-sm text-muted-foreground">{p.description}</p>
              </div>
            ))}
          </div>
        </Motion>
      ) : null}
    </div>
  );
}
