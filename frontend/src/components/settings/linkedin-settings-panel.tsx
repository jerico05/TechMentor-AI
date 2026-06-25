"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { AlertCircle, Briefcase, FileUp, Loader2, RefreshCw } from "lucide-react";
import * as React from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAppReady } from "@/lib/use-app-ready";
import { analyzeLinkedIn, fetchLinkedInAnalysis } from "@/services/linkedin";
import { invalidateDashboardSummary } from "@/services/dashboard";
import { fetchMyProfile } from "@/services/profile";
import { isApiError } from "@/services/api";

function linkedInStatusLabel(status: string): { label: string; className: string } {
  switch (status) {
    case "completed":
      return { label: "Analyse terminée", className: "text-green-600" };
    case "processing":
      return { label: "Analyse en cours…", className: "text-amber-600" };
    case "failed":
      return { label: "Échec de l'analyse", className: "text-destructive" };
    default:
      return { label: status, className: "text-muted-foreground" };
  }
}

export function LinkedInSettingsPanel() {
  const queryClient = useQueryClient();
  const appReady = useAppReady();
  const pdfInputRef = React.useRef<HTMLInputElement>(null);
  const { data: profile } = useQuery({
    queryKey: ["profile", "me"],
    queryFn: fetchMyProfile,
    enabled: appReady,
  });
  const { data: analysis, isLoading } = useQuery({
    queryKey: ["linkedin", "me"],
    queryFn: fetchLinkedInAnalysis,
    enabled: appReady,
  });
  const [url, setUrl] = React.useState("");
  const [profileText, setProfileText] = React.useState("");
  const [pdfFile, setPdfFile] = React.useState<File | null>(null);

  React.useEffect(() => {
    if (profile?.linkedin_url) setUrl(profile.linkedin_url);
  }, [profile?.linkedin_url]);

  const mutation = useMutation({
    mutationFn: () => analyzeLinkedIn(url || undefined, profileText || undefined, pdfFile),
    onSuccess: () => {
      setPdfFile(null);
      if (pdfInputRef.current) pdfInputRef.current.value = "";
      queryClient.invalidateQueries({ queryKey: ["linkedin", "me"] });
      queryClient.invalidateQueries({ queryKey: ["profile", "me"] });
      invalidateDashboardSummary(queryClient);
    },
  });

  const statusInfo = analysis ? linkedInStatusLabel(analysis.status) : null;
  const isProcessing = analysis?.status === "processing" || mutation.isPending;

  return (
    <div className="space-y-6">
      <div className="glass-card space-y-4 p-6">
        <p className="text-sm text-muted-foreground">
          Importez votre parcours LinkedIn pour que le mentor connaisse vos expériences et compétences.
        </p>

        <div className="rounded-2xl border border-primary/20 bg-primary/5 px-4 py-3 text-sm text-[hsl(var(--navy))]">
          <p className="font-semibold">Méthode recommandée (fiable à 100 %)</p>
          <ol className="mt-2 list-decimal space-y-1 pl-4 text-muted-foreground">
            <li>Ouvrez votre profil LinkedIn sur ordinateur</li>
            <li>Cliquez sur <strong className="text-foreground">Plus</strong> puis{" "}
              <strong className="text-foreground">Enregistrer au format PDF</strong></li>
            <li>Importez ce PDF ci-dessous avec votre URL de profil</li>
          </ol>
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="linkedin-url">URL LinkedIn</Label>
          <Input
            id="linkedin-url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://linkedin.com/in/votre-profil"
            className="input-modern"
          />
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="linkedin-pdf">Export PDF LinkedIn</Label>
          <Input
            id="linkedin-pdf"
            ref={pdfInputRef}
            type="file"
            accept="application/pdf,.pdf"
            className="input-modern cursor-pointer file:mr-3 file:rounded-xl file:border-0 file:bg-primary/10 file:px-3 file:py-2 file:text-sm file:font-semibold file:text-primary"
            onChange={(e) => setPdfFile(e.target.files?.[0] ?? null)}
          />
          {pdfFile ? (
            <p className="text-xs text-green-600">Fichier sélectionné : {pdfFile.name}</p>
          ) : (
            <p className="text-xs text-muted-foreground">
              Sans PDF, nous essayons l&apos;extraction automatique (souvent bloquée par LinkedIn).
            </p>
          )}
        </div>

        <details className="rounded-xl border border-[#e2e8f0] bg-white/50 px-4 py-3 text-sm">
          <summary className="cursor-pointer font-medium text-[hsl(var(--navy))]">
            Autre option : coller le texte du profil
          </summary>
          <textarea
            id="linkedin-text"
            rows={5}
            value={profileText}
            onChange={(e) => setProfileText(e.target.value)}
            placeholder="Expériences, formations, compétences..."
            className="input-modern mt-3 min-h-[100px] w-full resize-y py-3"
          />
        </details>

        <Button
          onClick={() => mutation.mutate()}
          disabled={isProcessing || !url.trim()}
          className="rounded-2xl"
        >
          {isProcessing ? (
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          ) : pdfFile ? (
            <FileUp className="mr-2 h-4 w-4" />
          ) : (
            <Briefcase className="mr-2 h-4 w-4" />
          )}
          {isProcessing
            ? "Analyse en cours…"
            : pdfFile
              ? "Analyser le PDF LinkedIn"
              : "Analyser mon LinkedIn"}
        </Button>
        {mutation.isError && (
          <p className="text-sm text-destructive">
            {isApiError(mutation.error) ? mutation.error.error.message : "Analyse impossible."}
          </p>
        )}
      </div>

      {isLoading ? (
        <div className="flex justify-center py-6">
          <Loader2 className="h-6 w-6 animate-spin" />
        </div>
      ) : analysis ? (
        <div className="glass-card space-y-4 p-6">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <p className={`text-sm font-medium ${statusInfo?.className}`}>{statusInfo?.label}</p>
            {analysis.status === "processing" && <Loader2 className="h-4 w-4 animate-spin text-amber-600" />}
          </div>

          {analysis.status === "failed" && (
            <div className="flex items-start gap-2 rounded-xl border border-destructive/30 bg-destructive/10 p-4 text-sm text-destructive">
              <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
              <div>
                <p className="font-medium">Extraction automatique impossible.</p>
                <p className="mt-1 text-destructive/80">
                  Utilisez l&apos;export PDF LinkedIn (Profil &gt; Plus &gt; Enregistrer au format PDF)
                  puis relancez l&apos;analyse.
                </p>
              </div>
            </div>
          )}

          {analysis.status === "completed" && (
            <div className="space-y-4">
              {analysis.headline ? (
                <div>
                  <p className="text-sm text-muted-foreground">Titre</p>
                  <p className="font-semibold">{analysis.headline}</p>
                </div>
              ) : null}
              {analysis.summary ? (
                <div>
                  <p className="text-sm text-muted-foreground">Résumé du parcours</p>
                  <p className="text-sm leading-relaxed">{analysis.summary}</p>
                </div>
              ) : null}
              {(analysis.experiences?.length ?? 0) > 0 ? (
                <div>
                  <p className="mb-2 text-sm font-medium">Expériences</p>
                  <ul className="space-y-2 text-sm">
                    {analysis.experiences!.slice(0, 5).map((exp, i) => (
                      <li key={`${exp.title}-${i}`} className="rounded-xl bg-secondary/50 px-3 py-2">
                        <span className="font-medium">{exp.title}</span>
                        {exp.company ? ` · ${exp.company}` : ""}
                        {exp.duration ? (
                          <span className="block text-xs text-muted-foreground">{exp.duration}</span>
                        ) : null}
                      </li>
                    ))}
                  </ul>
                </div>
              ) : null}
              {(analysis.skills?.length ?? 0) > 0 ? (
                <div>
                  <p className="mb-2 text-sm font-medium">Compétences</p>
                  <div className="flex flex-wrap gap-2">
                    {analysis.skills!.map((skill) => (
                      <span
                        key={skill}
                        className="rounded-full bg-primary/10 px-3 py-1 text-sm font-medium text-primary"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              ) : null}
            </div>
          )}

          <Button
            variant="outline"
            size="sm"
            onClick={() => mutation.mutate()}
            disabled={isProcessing || !url.trim()}
            className="w-full rounded-xl sm:w-auto"
          >
            <RefreshCw className="mr-2 h-4 w-4" /> Actualiser
          </Button>
        </div>
      ) : null}
    </div>
  );
}
