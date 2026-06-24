"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { AlertCircle, FileUp, Loader2, Upload } from "lucide-react";
import * as React from "react";

import { Button } from "@/components/ui/button";
import { useAppReady } from "@/lib/use-app-ready";
import { fetchMyCV, uploadCV } from "@/services/cv";
import { invalidateDashboardSummary } from "@/services/dashboard";
import { isApiError } from "@/services/api";

const MAX_CV_BYTES = 5 * 1024 * 1024;

function cvStatusLabel(status: string): { label: string; className: string } {
  switch (status) {
    case "parsed":
      return { label: "Analysé", className: "text-green-600" };
    case "processing":
      return { label: "Analyse en cours…", className: "text-amber-600" };
    case "failed":
      return { label: "Échec de l'analyse", className: "text-destructive" };
    default:
      return { label: status, className: "text-muted-foreground" };
  }
}

export function CVSettingsPanel() {
  const queryClient = useQueryClient();
  const appReady = useAppReady();
  const inputRef = React.useRef<HTMLInputElement>(null);
  const [clientError, setClientError] = React.useState<string | null>(null);

  const { data: cv, isLoading } = useQuery({
    queryKey: ["cv", "me"],
    queryFn: fetchMyCV,
    enabled: appReady,
    refetchInterval: (q) => (q.state.data?.status === "processing" ? 2000 : false),
  });

  const mutation = useMutation({
    mutationFn: uploadCV,
    onSuccess: () => {
      setClientError(null);
      queryClient.invalidateQueries({ queryKey: ["cv", "me"] });
      invalidateDashboardSummary(queryClient);
    },
  });

  function onFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;

    const ext = file.name.toLowerCase();
    if (!ext.endsWith(".pdf") && !ext.endsWith(".docx")) {
      setClientError("Format accepté : PDF ou DOCX uniquement.");
      return;
    }
    if (file.size > MAX_CV_BYTES) {
      setClientError("Fichier trop volumineux (max 5 Mo).");
      return;
    }

    setClientError(null);
    mutation.mutate(file);
  }

  const statusInfo = cv ? cvStatusLabel(cv.status) : null;

  return (
    <div className="space-y-6">
      <div className="glass-card p-8 text-center">
        <input ref={inputRef} type="file" accept=".pdf,.docx" className="hidden" onChange={onFileChange} />
        <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/10">
          <Upload className="h-8 w-8 text-primary" />
        </div>
        <p className="mb-1 text-sm font-medium text-[hsl(var(--navy))]">Téléverser votre CV</p>
        <p className="mb-4 text-sm text-muted-foreground">PDF ou DOCX (max 5 Mo)</p>
        <Button
          onClick={() => inputRef.current?.click()}
          disabled={mutation.isPending || cv?.status === "processing"}
          className="btn-glow rounded-2xl"
        >
          {mutation.isPending || cv?.status === "processing" ? (
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          ) : (
            <FileUp className="mr-2 h-4 w-4" />
          )}
          {mutation.isPending || cv?.status === "processing" ? "Analyse en cours…" : "Choisir un fichier"}
        </Button>
        {clientError && <p className="mt-4 text-sm text-destructive">{clientError}</p>}
        {mutation.isError && (
          <p className="mt-4 text-sm text-destructive">
            {isApiError(mutation.error) ? mutation.error.error.message : "Erreur d'upload."}
          </p>
        )}
      </div>

      {isLoading ? (
        <div className="flex justify-center py-6">
          <Loader2 className="h-6 w-6 animate-spin text-primary" />
        </div>
      ) : cv ? (
        <div className="glass-card p-6">
          <h3 className="break-all font-semibold">{cv.original_filename}</h3>
          <p className={`mt-1 text-sm font-medium ${statusInfo?.className}`}>
            Statut : {statusInfo?.label}
          </p>

          {cv.status === "failed" && (
            <div className="mt-4 flex items-start gap-2 rounded-xl border border-destructive/30 bg-destructive/10 p-4 text-sm text-destructive">
              <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
              <div>
                <p className="font-medium">L&apos;analyse du CV a échoué.</p>
                <p className="mt-1 text-destructive/80">
                  Utilisez un PDF exporté (texte sélectionnable), pas une photo scannée. Réessayez avec un autre fichier.
                </p>
              </div>
            </div>
          )}

          {cv.status === "processing" && (
            <div className="mt-4 space-y-2">
              <div className="flex items-center gap-2 text-sm text-amber-600">
                <Loader2 className="h-4 w-4 animate-spin" />
                Extraction du texte et des compétences…
              </div>
              <p className="text-xs text-muted-foreground">
                Cela prend en général quelques secondes. Si le statut ne change pas, rechargez la page.
              </p>
            </div>
          )}

          {cv.status === "parsed" && (
            <p className="mt-2 text-sm font-medium text-green-600">CV analysé avec succès.</p>
          )}

          {cv.extracted_text && cv.status === "parsed" && (
            <p className="mt-4 max-h-48 overflow-y-auto rounded-xl bg-secondary/50 p-4 text-sm leading-relaxed">
              {cv.extracted_text.slice(0, 600)}
              {cv.extracted_text.length > 600 ? "…" : ""}
            </p>
          )}
        </div>
      ) : null}
    </div>
  );
}
