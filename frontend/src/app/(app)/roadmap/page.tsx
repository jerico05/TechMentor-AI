"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Loader2, Map, Sparkles } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Motion } from "@/components/ui/motion";
import { fetchActiveRoadmap, generateRoadmap } from "@/services/roadmap";
import { isApiError } from "@/services/api";

export default function RoadmapPage() {
  const queryClient = useQueryClient();
  const { data: roadmap, isLoading } = useQuery({
    queryKey: ["roadmap", "me"],
    queryFn: fetchActiveRoadmap,
  });

  const mutation = useMutation({
    mutationFn: () => generateRoadmap(),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["roadmap", "me"] }),
  });

  const active = mutation.data ?? roadmap;

  return (
    <div className="mx-auto max-w-3xl">
      <Motion animation="slide-up" delay={1} className="mb-6 flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-[hsl(var(--navy))]">Roadmap</h1>
          <p className="text-muted-foreground">Plan d&apos;apprentissage personnalisé sur 3 mois.</p>
        </div>
        <Button onClick={() => mutation.mutate()} disabled={mutation.isPending} className="btn-glow rounded-2xl">
          {mutation.isPending ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Sparkles className="mr-2 h-4 w-4" />}
          {active ? "Régénérer" : "Générer"}
        </Button>
      </Motion>

      {mutation.isError && (
        <p className="mb-4 text-sm text-destructive">
          {isApiError(mutation.error) ? mutation.error.error.message : "Génération impossible."}
        </p>
      )}

      {isLoading && !active ? (
        <div className="flex justify-center py-16"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>
      ) : active?.content ? (
        <Motion animation="scale-in" delay={2} className="space-y-4">
          {active.content.summary && (
            <div className="glass-card p-5 text-sm leading-relaxed text-muted-foreground">
              {active.content.summary}
            </div>
          )}
          {(active.content.months ?? []).map((month) => (
            <div key={month.month} className="glass-card-interactive p-6">
              <div className="mb-3 flex items-center gap-2">
                <Map className="h-5 w-5 text-primary" />
                <h2 className="text-lg font-bold">Mois {month.month} — {month.title}</h2>
              </div>
              <div className="mb-3 flex flex-wrap gap-2">
                {month.skills?.map((s) => (
                  <span key={s} className="rounded-full bg-primary/10 px-3 py-1 text-xs font-medium text-primary">{s}</span>
                ))}
              </div>
              <ul className="list-inside list-disc space-y-1 text-sm text-muted-foreground">
                {month.actions?.map((a) => <li key={a}>{a}</li>)}
              </ul>
            </div>
          ))}
        </Motion>
      ) : (
        <div className="glass-card p-12 text-center text-muted-foreground">
          Lancez d&apos;abord une analyse skill gap, puis générez votre roadmap.
        </div>
      )}
    </div>
  );
}
