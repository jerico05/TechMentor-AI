"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Loader2, Trash2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { useAppReady } from "@/lib/use-app-ready";
import { invalidateDashboardSummary } from "@/services/dashboard";
import { deleteMyProfile, fetchMyProfile } from "@/services/profile";

export function ProfileDangerZone() {
  const queryClient = useQueryClient();
  const appReady = useAppReady();
  const { data: profile, isLoading } = useQuery({
    queryKey: ["profile", "me"],
    queryFn: fetchMyProfile,
    enabled: appReady,
  });

  const deleteMutation = useMutation({
    mutationFn: deleteMyProfile,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["profile", "me"] });
      invalidateDashboardSummary(queryClient);
    },
  });

  if (isLoading || !profile) return null;

  return (
    <div className="glass-card border border-destructive/20 p-6">
      <h3 className="font-semibold text-destructive">Zone de danger</h3>
      <p className="mt-1 text-sm text-muted-foreground">
        Supprime votre profil étudiant et les données associées dans l&apos;application.
        Votre compte de connexion reste actif.
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
  );
}
