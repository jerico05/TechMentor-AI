"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { FileUp, Loader2, Upload } from "lucide-react";
import * as React from "react";

import { Button } from "@/components/ui/button";
import { Motion } from "@/components/ui/motion";
import { fetchMyCV, uploadCV } from "@/services/cv";
import { isApiError } from "@/services/api";

export default function CVPage() {
  const queryClient = useQueryClient();
  const inputRef = React.useRef<HTMLInputElement>(null);
  const { data: cv, isLoading } = useQuery({
    queryKey: ["cv", "me"],
    queryFn: fetchMyCV,
    refetchInterval: (q) => (q.state.data?.status === "processing" ? 2000 : false),
  });

  const mutation = useMutation({
    mutationFn: uploadCV,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["cv", "me"] }),
  });

  function onFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (file) mutation.mutate(file);
  }

  return (
    <div className="mx-auto max-w-2xl">
      <Motion animation="slide-up" delay={1} className="mb-6">
        <h1 className="text-3xl font-extrabold tracking-tight text-[hsl(var(--navy))]">Mon CV</h1>
        <p className="text-muted-foreground">Téléversez votre CV pour extraire automatiquement vos compétences.</p>
      </Motion>

      <Motion animation="scale-in" delay={2}>
        <div className="glass-card p-8 text-center">
          <input ref={inputRef} type="file" accept=".pdf,.docx" className="hidden" onChange={onFileChange} />
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/10">
            <Upload className="h-8 w-8 text-primary" />
          </div>
          <p className="mb-4 text-sm text-muted-foreground">PDF ou DOCX — max 5 Mo</p>
          <Button
            onClick={() => inputRef.current?.click()}
            disabled={mutation.isPending}
            className="btn-glow rounded-2xl"
          >
            {mutation.isPending ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <FileUp className="mr-2 h-4 w-4" />
            )}
            {mutation.isPending ? "Analyse en cours…" : "Choisir un fichier"}
          </Button>
          {mutation.isError && (
            <p className="mt-4 text-sm text-destructive">
              {isApiError(mutation.error) ? mutation.error.error.message : "Erreur d'upload."}
            </p>
          )}
        </div>
      </Motion>

      {isLoading ? (
        <div className="mt-6 flex justify-center"><Loader2 className="h-6 w-6 animate-spin text-primary" /></div>
      ) : cv ? (
        <Motion animation="slide-up" delay={3} className="glass-card mt-6 p-6">
          <h2 className="font-semibold">{cv.original_filename}</h2>
          <p className="mt-1 text-sm text-muted-foreground">Statut : {cv.status}</p>
          {cv.extracted_text && (
            <p className="mt-4 max-h-48 overflow-y-auto rounded-xl bg-secondary/50 p-4 text-sm leading-relaxed">
              {cv.extracted_text.slice(0, 600)}
              {cv.extracted_text.length > 600 ? "…" : ""}
            </p>
          )}
        </Motion>
      ) : null}
    </div>
  );
}
