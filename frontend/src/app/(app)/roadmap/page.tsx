"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Loader2, Sparkles } from "lucide-react";
import { useState } from "react";

import { RoadmapInfographic } from "@/components/roadmap/roadmap-infographic";
import { Button } from "@/components/ui/button";
import { Motion } from "@/components/ui/motion";
import { useAppReady } from "@/lib/use-app-ready";
import { buildPreviewMonths } from "@/lib/roadmap-infographic";
import { ROADMAP_DURATION_LABELS, ROADMAP_DURATION_OPTIONS } from "@/lib/roadmap-duration";
import { fetchActiveRoadmap, fetchRoadmapSuggestion, generateRoadmap } from "@/services/roadmap";
import { invalidateDashboardSummary } from "@/services/dashboard";
import { isApiError } from "@/services/api";
import type { RoadmapDurationMonths } from "@/types";
import { cn } from "@/lib/utils";

export default function RoadmapPage() {
  const queryClient = useQueryClient();
  const appReady = useAppReady();
  const [durationOverride, setDurationOverride] = useState<RoadmapDurationMonths | null>(null);

  const { data: roadmap, isLoading } = useQuery({
    queryKey: ["roadmap", "me"],
    queryFn: fetchActiveRoadmap,
    enabled: appReady,
  });

  const { data: suggestion, isLoading: suggestionLoading } = useQuery({
    queryKey: ["roadmap", "suggestion"],
    queryFn: fetchRoadmapSuggestion,
    enabled: appReady,
  });

  const selectedDuration = durationOverride ?? suggestion?.suggested_months ?? 6;

  const mutation = useMutation({
    mutationFn: () => generateRoadmap({ durationMonths: selectedDuration }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["roadmap", "me"] });
      invalidateDashboardSummary(queryClient);
    },
  });

  const active = mutation.data ?? roadmap;
  const generatedMonths = active?.content?.months ?? [];
  const isGeneratedForSelection =
    generatedMonths.length > 0 && generatedMonths.length === selectedDuration;
  const displayMonths = isGeneratedForSelection
    ? generatedMonths
    : buildPreviewMonths(selectedDuration);

  return (
    <div className="mx-auto max-w-6xl">
      <Motion animation="slide-up" delay={1} className="mb-6 flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-[hsl(var(--navy))]">Roadmap</h1>
          <p className="text-muted-foreground">Plan d&apos;apprentissage personnalisé, étape par étape.</p>
        </div>
        <Button onClick={() => mutation.mutate()} disabled={mutation.isPending} className="btn-glow rounded-2xl">
          {mutation.isPending ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Sparkles className="mr-2 h-4 w-4" />}
          {active ? "Régénérer" : "Générer"}
        </Button>
      </Motion>

      <Motion animation="fade-in" delay={2} className="mb-6 rounded-[1.5rem] border border-white/70 bg-white/80 p-4 shadow-crextio sm:p-5">
        <p className="text-sm font-semibold text-[hsl(var(--navy))]">Durée du parcours</p>
        <div className="mt-3 flex flex-wrap gap-2">
          {ROADMAP_DURATION_OPTIONS.map((months) => {
            const isSelected = selectedDuration === months;
            const isRecommended = suggestion?.suggested_months === months;
            return (
              <button
                key={months}
                type="button"
                onClick={() => setDurationOverride(months)}
                className={cn(
                  "relative rounded-2xl border px-4 py-2.5 text-sm font-semibold transition-all",
                  isSelected
                    ? "border-[hsl(var(--navy))] bg-[hsl(var(--navy))] text-white shadow-md"
                    : "border-[#e2e8f0] bg-white text-[hsl(var(--navy))] hover:border-[hsl(var(--navy))]/30 hover:bg-[#f8fafc]",
                )}
              >
                {ROADMAP_DURATION_LABELS[months]}
                {isRecommended ? (
                  <span
                    className={cn(
                      "ml-2 rounded-full px-2 py-0.5 text-[10px] font-bold uppercase tracking-wide",
                      isSelected ? "bg-white/20 text-white" : "bg-[#e8f5ee] text-[#2d8a5c]",
                    )}
                  >
                    Recommandé
                  </span>
                ) : null}
              </button>
            );
          })}
        </div>
        <p className="mt-3 text-sm text-muted-foreground">
          {suggestionLoading
            ? "Calcul de la durée recommandée..."
            : suggestion?.reason ?? "Choisissez la durée : la route et les étapes s'adaptent en direct."}
        </p>
      </Motion>

      {mutation.isError && (
        <p className="mb-4 text-sm text-destructive">
          {isApiError(mutation.error) ? mutation.error.error.message : "Génération impossible."}
        </p>
      )}

      {isLoading && !active ? (
        <div className="flex justify-center py-16">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      ) : (
        <Motion animation="scale-in" delay={2}>
          <RoadmapInfographic
            key={selectedDuration}
            months={displayMonths}
            summary={isGeneratedForSelection ? active?.content?.summary : undefined}
            isPreview={!isGeneratedForSelection}
          />
        </Motion>
      )}
    </div>
  );
}
