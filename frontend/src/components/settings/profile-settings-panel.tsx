"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useForm, Controller } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { Loader2, Save, Trash2 } from "lucide-react";

import { CareerSelect } from "@/components/careers/career-select";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ModernSelect } from "@/components/ui/modern-select";
import { useAppReady } from "@/lib/use-app-ready";
import { ACADEMIC_LEVEL_GROUP_ORDER, ACADEMIC_LEVEL_OPTIONS } from "@/lib/academic-levels";
import { fetchCareers } from "@/services/careers";
import { invalidateDashboardSummary } from "@/services/dashboard";
import {
  computeProfileProgress,
  deleteMyProfile,
  fetchMyProfile,
  upsertMyProfile,
} from "@/services/profile";
import type { AcademicLevel } from "@/types";

const schema = z.object({
  university: z.string().optional(),
  department: z.string().optional(),
  academic_level: z.enum(["licence1", "licence2", "licence3", "master1", "master2", "other"]),
  career_goal: z.string().optional(),
  career_path_id: z.coerce.number().optional().nullable(),
  github_url: z.string().url("URL invalide").optional().or(z.literal("")),
  bio: z.string().max(2000).optional(),
});

type FormData = z.infer<typeof schema>;

export function ProfileSettingsPanel() {
  const queryClient = useQueryClient();
  const appReady = useAppReady();
  const { data: profile, isLoading } = useQuery({
    queryKey: ["profile", "me"],
    queryFn: fetchMyProfile,
    enabled: appReady,
  });
  const { data: careers, isLoading: careersLoading } = useQuery({
    queryKey: ["careers"],
    queryFn: fetchCareers,
    staleTime: 10 * 60 * 1000,
    enabled: appReady,
  });

  const {
    register,
    handleSubmit,
    control,
    formState: { errors },
  } = useForm<FormData>({
    resolver: zodResolver(schema),
    values: {
      university: profile?.university ?? "",
      department: profile?.department ?? "",
      academic_level: profile?.academic_level ?? "licence3",
      career_goal: profile?.career_goal ?? "",
      career_path_id: profile?.career_path_id ?? undefined,
      github_url: profile?.github_url ?? "",
      bio: profile?.bio ?? "",
    },
  });

  const mutation = useMutation({
    mutationFn: upsertMyProfile,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["profile", "me"] });
      invalidateDashboardSummary(queryClient);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: deleteMyProfile,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["profile", "me"] });
      invalidateDashboardSummary(queryClient);
    },
  });

  const progress = computeProfileProgress(profile ?? null);

  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <Loader2 className="h-7 w-7 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="glass-card-interactive p-5">
        <div className="mb-2 flex justify-between text-sm font-medium">
          <span>Complétion du profil</span>
          <span className="font-bold text-primary">{progress}%</span>
        </div>
        <div className="h-2.5 overflow-hidden rounded-full bg-secondary">
          <div
            className="progress-bar-fill h-full rounded-full bg-gradient-to-r from-primary to-accent"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      <form
        onSubmit={handleSubmit((data) =>
          mutation.mutate({
            ...data,
            github_url: data.github_url || null,
            university: data.university || null,
            department: data.department || null,
            career_goal: data.career_goal || null,
            career_path_id: data.career_path_id || null,
            bio: data.bio || null,
          }),
        )}
        className="glass-card space-y-5 p-6 sm:p-8"
      >
        <div className="grid gap-4 sm:grid-cols-2">
          <div className="space-y-1.5">
            <Label htmlFor="university">Université</Label>
            <Input id="university" {...register("university")} placeholder="Ex. Université de Lomé" />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="department">Filière / Département</Label>
            <Input id="department" {...register("department")} placeholder="Ex. Informatique" />
          </div>
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="academic_level">Niveau</Label>
          <Controller
            name="academic_level"
            control={control}
            render={({ field }) => (
              <ModernSelect<AcademicLevel>
                id="academic_level"
                value={field.value}
                onChange={field.onChange}
                options={ACADEMIC_LEVEL_OPTIONS}
                groupOrder={ACADEMIC_LEVEL_GROUP_ORDER}
                placeholder="Sélectionner votre niveau"
              />
            )}
          />
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="career_path_id">Métier cible</Label>
          <Controller
            name="career_path_id"
            control={control}
            render={({ field }) => (
              <CareerSelect
                id="career_path_id"
                value={field.value ?? null}
                onChange={(id) => field.onChange(id ?? undefined)}
                careers={careers ?? []}
                loading={careersLoading}
                placeholder="Choisir un métier"
              />
            )}
          />
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="career_goal">Objectif carrière</Label>
          <Input id="career_goal" {...register("career_goal")} placeholder="Ex. Développeur fullstack" />
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="github_url">URL GitHub (profil)</Label>
          <Input id="github_url" {...register("github_url")} placeholder="https://github.com/vous" />
          {errors.github_url && (
            <p className="text-xs text-destructive">{errors.github_url.message}</p>
          )}
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="bio">Bio</Label>
          <textarea
            id="bio"
            rows={4}
            className="input-modern min-h-[100px] resize-y py-3"
            {...register("bio")}
            placeholder="Parlez de vos projets, compétences et ambitions..."
          />
        </div>

        {mutation.isSuccess && (
          <p className="text-sm font-medium text-green-600">Profil enregistré avec succès.</p>
        )}
        {mutation.isError && (
          <p className="text-sm text-destructive">Erreur lors de l&apos;enregistrement.</p>
        )}

        <Button type="submit" disabled={mutation.isPending} className="btn-glow rounded-2xl">
          {mutation.isPending ? (
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          ) : (
            <Save className="mr-2 h-4 w-4" />
          )}
          Enregistrer le profil
        </Button>
      </form>

      {profile ? (
        <div className="glass-card border border-destructive/20 p-6">
          <h3 className="font-semibold text-destructive">Zone de danger</h3>
          <p className="mt-1 text-sm text-muted-foreground">
            Supprime votre profil étudiant. Votre compte reste actif.
          </p>
          {deleteMutation.isError && (
            <p className="mt-2 text-sm text-destructive">Impossible de supprimer le profil.</p>
          )}
          {deleteMutation.isSuccess && (
            <p className="mt-2 text-sm font-medium text-green-600">Profil supprimé.</p>
          )}
          <Button
            type="button"
            variant="outline"
            disabled={deleteMutation.isPending}
            className="mt-4 rounded-2xl border-destructive/40 text-destructive hover:bg-destructive/10"
            onClick={() => {
              if (window.confirm("Supprimer votre profil étudiant ? Cette action est irréversible.")) {
                deleteMutation.mutate();
              }
            }}
          >
            {deleteMutation.isPending ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <Trash2 className="mr-2 h-4 w-4" />
            )}
            Supprimer mon profil
          </Button>
        </div>
      ) : null}
    </div>
  );
}
