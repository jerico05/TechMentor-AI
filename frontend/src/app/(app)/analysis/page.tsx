"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { BarChart3, CheckCircle2, Loader2, XCircle } from "lucide-react";
import * as React from "react";

import { CareerSelect } from "@/components/careers/career-select";
import { Button } from "@/components/ui/button";
import { Motion } from "@/components/ui/motion";
import { useAppReady } from "@/lib/use-app-ready";
import { fetchLatestAnalysis, levelLabel, runAnalysis } from "@/services/analysis";
import { fetchCareers } from "@/services/careers";
import { invalidateDashboardSummary } from "@/services/dashboard";
import { fetchMyProfile } from "@/services/profile";
import { isApiError } from "@/services/api";

export default function AnalysisPage() {
  const queryClient = useQueryClient();
  const appReady = useAppReady();
  const { data: careers, isLoading: careersLoading } = useQuery({
    queryKey: ["careers"],
    queryFn: fetchCareers,
    staleTime: 10 * 60 * 1000,
    enabled: appReady,
  });
  const { data: profile } = useQuery({
    queryKey: ["profile", "me"],
    queryFn: fetchMyProfile,
    enabled: appReady,
  });
  const { data: analysis, isLoading } = useQuery({
    queryKey: ["analysis", "me"],
    queryFn: fetchLatestAnalysis,
    enabled: appReady,
  });
  const [careerId, setCareerId] = React.useState<number | "">("");

  React.useEffect(() => {
    if (profile?.career_path_id) setCareerId(profile.career_path_id);
  }, [profile?.career_path_id]);

  const mutation = useMutation({
    mutationFn: () => runAnalysis(typeof careerId === "number" ? careerId : undefined),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["analysis", "me"] });
      queryClient.invalidateQueries({ queryKey: ["analysis", "history"] });
      queryClient.invalidateQueries({ queryKey: ["profile", "me"] });
      queryClient.invalidateQueries({ queryKey: ["projects", "recommendations"] });
      queryClient.invalidateQueries({ queryKey: ["roadmap", "suggestion"] });
      invalidateDashboardSummary(queryClient);
    },
  });

  const result = mutation.data ?? analysis;

  return (
    <div className="mx-auto max-w-3xl">
      <Motion animation="slide-up" delay={1} className="mb-6">
        <h1 className="text-3xl font-extrabold tracking-tight text-[hsl(var(--navy))]">Skill Gap</h1>
        <p className="text-muted-foreground">Comparez vos compétences à votre métier cible et obtenez votre score.</p>
      </Motion>

      <Motion animation="scale-in" delay={2} className="glass-card space-y-4 p-6">
        <label className="text-sm font-medium text-[hsl(var(--navy))]">Métier cible</label>
        <CareerSelect
          value={typeof careerId === "number" ? careerId : null}
          onChange={(id) => setCareerId(id ?? "")}
          careers={careers ?? []}
          loading={careersLoading}
        />
        <Button
          onClick={() => mutation.mutate()}
          disabled={mutation.isPending || !careerId}
          className="btn-glow w-full rounded-2xl sm:w-auto"
        >
          {mutation.isPending ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <BarChart3 className="mr-2 h-4 w-4" />}
          Lancer l&apos;analyse
        </Button>
        {mutation.isError && (
          <p className="text-sm text-destructive">
            {isApiError(mutation.error) ? mutation.error.error.message : "Erreur d'analyse."}
          </p>
        )}
      </Motion>

      {isLoading && !result ? (
        <div className="mt-8 flex justify-center"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>
      ) : result ? (
        <Motion animation="slide-up" delay={3} className="mt-6 space-y-4">
          <div className="glass-card-interactive p-6 text-center">
            <p className="text-sm text-muted-foreground">Préparation métier (écarts de compétences)</p>
            <p className="text-5xl font-extrabold text-primary">{result.score}<span className="text-2xl">/100</span></p>
            <p className="mt-4 text-sm text-muted-foreground">Niveau d&apos;expérience</p>
            <p className="text-xl font-bold text-[hsl(var(--navy))]">{levelLabel(result.level)}</p>
            {result.projects_completed !== undefined && (
              <p className="mt-1 text-xs text-muted-foreground">
                {result.projects_completed} projet{result.projects_completed !== 1 ? "s" : ""} enregistré
                {result.projects_completed !== 1 ? "s" : ""} · ajoutez-en dans Paramètres → Projets
              </p>
            )}
            {result.level_reason && (
              <p className="mt-3 text-xs leading-relaxed text-muted-foreground">{result.level_reason}</p>
            )}
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            <SkillList title="Acquises" skills={result.owned_skills} icon={CheckCircle2} variant="owned" />
            <SkillList title="À développer" skills={result.missing_skills} icon={XCircle} variant="missing" />
          </div>
        </Motion>
      ) : null}
    </div>
  );
}

function SkillList({
  title,
  skills,
  icon: Icon,
  variant,
}: {
  title: string;
  skills: string[];
  icon: React.ComponentType<{ className?: string }>;
  variant: "owned" | "missing";
}) {
  return (
    <div className="glass-card p-5">
      <h3 className="mb-3 flex items-center gap-2 font-semibold">
        <Icon className={variant === "owned" ? "text-green-600" : "text-orange-500"} />
        {title}
      </h3>
      <ul className="space-y-1.5">
        {skills.length === 0 ? (
          <li className="text-sm text-muted-foreground">Aucune</li>
        ) : (
          skills.map((s) => (
            <li key={s} className="rounded-lg bg-secondary/50 px-3 py-1.5 text-sm">{s}</li>
          ))
        )}
      </ul>
    </div>
  );
}
