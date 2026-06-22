"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { Loader2, Save, UserCircle } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Motion } from "@/components/ui/motion";
import { computeProfileProgress, fetchMyProfile, upsertMyProfile } from "@/services/profile";
import { fetchCareers } from "@/services/careers";
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

const LEVELS: { value: AcademicLevel; label: string }[] = [
  { value: "licence1", label: "Licence 1" },
  { value: "licence2", label: "Licence 2" },
  { value: "licence3", label: "Licence 3" },
  { value: "master1", label: "Master 1" },
  { value: "master2", label: "Master 2" },
  { value: "other", label: "Autre" },
];

export default function ProfilePage() {
  const queryClient = useQueryClient();
  const { data: profile, isLoading } = useQuery({
    queryKey: ["profile", "me"],
    queryFn: fetchMyProfile,
  });
  const { data: careers } = useQuery({ queryKey: ["careers"], queryFn: fetchCareers, staleTime: 60_000 });

  const {
    register,
    handleSubmit,
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
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["profile", "me"] }),
  });

  const progress = computeProfileProgress(profile ?? null);

  if (isLoading) {
    return (
      <div className="flex min-h-[40vh] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl">
      <Motion animation="slide-up" delay={1} className="mb-6">
        <div className="flex items-center gap-3">
          <span className="flex h-10 w-10 items-center justify-center rounded-2xl bg-gradient-to-br from-primary to-accent text-white shadow-lg shadow-primary/25">
            <UserCircle className="h-5 w-5" />
          </span>
          <div>
            <h1 className="text-3xl font-extrabold tracking-tight text-[hsl(var(--navy))]">Profil étudiant</h1>
            <p className="text-muted-foreground">Complétez votre profil pour un mentorat personnalisé.</p>
          </div>
        </div>
        <div className="glass-card-interactive mt-5 p-5">
          <div className="mb-2 flex justify-between text-sm font-medium">
            <span>Complétion</span>
            <span className="font-bold text-primary">{progress}%</span>
          </div>
          <div className="h-2.5 overflow-hidden rounded-full bg-secondary">
            <div
              className="progress-bar-fill h-full rounded-full bg-gradient-to-r from-primary to-accent"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      </Motion>

      <Motion animation="scale-in" delay={2}>
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
            <select
              id="academic_level"
              className="input-modern h-11 cursor-pointer"
              {...register("academic_level")}
            >
              {LEVELS.map((l) => (
                <option key={l.value} value={l.value}>
                  {l.label}
                </option>
              ))}
            </select>
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="career_path_id">Métier cible</Label>
            <select id="career_path_id" className="input-modern h-11 cursor-pointer" {...register("career_path_id")}>
              <option value="">— Choisir —</option>
              {careers?.map((c) => (
                <option key={c.id} value={c.id}>{c.name}</option>
              ))}
            </select>
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="career_goal">Objectif carrière</Label>
            <Input id="career_goal" {...register("career_goal")} placeholder="Ex. Développeur fullstack" />
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="github_url">GitHub</Label>
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
            <p className="animate-slide-down text-sm font-medium text-green-600">Profil enregistré avec succès.</p>
          )}
          {mutation.isError && (
            <p className="animate-slide-down text-sm text-destructive">Erreur lors de l&apos;enregistrement.</p>
          )}

          <Button type="submit" disabled={mutation.isPending} className="btn-glow rounded-2xl">
            {mutation.isPending ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <Save className="mr-2 h-4 w-4" />
            )}
            Enregistrer
          </Button>
        </form>
      </Motion>
    </div>
  );
}
