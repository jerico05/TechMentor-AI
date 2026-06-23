import { api } from "@/services/api";
import type { AnalysisResult } from "@/types";

export type { AnalysisResult } from "@/types";

export async function runAnalysis(careerPathId?: number): Promise<AnalysisResult> {
  const { data } = await api.post<AnalysisResult>("/analysis/run", {
    career_path_id: careerPathId ?? null,
  });
  return data;
}

export async function fetchLatestAnalysis(): Promise<AnalysisResult | null> {
  const { data } = await api.get<AnalysisResult | null>("/analysis/me");
  return data;
}

export async function fetchAnalysisHistory(): Promise<AnalysisResult[]> {
  const { data } = await api.get<AnalysisResult[]>("/analysis/history");
  return data;
}

const LEVEL_LABELS: Record<string, string> = {
  entry: "Entry level",
  intermediaire: "Intermédiaire",
  senior: "Senior",
  debutant: "Entry level",
  avance: "Senior",
};

export function levelLabel(level: string): string {
  return LEVEL_LABELS[level] ?? level;
}
