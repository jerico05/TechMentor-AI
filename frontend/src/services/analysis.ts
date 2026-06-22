import { api } from "@/services/api";

export interface AnalysisResult {
  id: number;
  career_path_id: number;
  score: number;
  level: string;
  owned_skills: string[];
  missing_skills: string[];
}

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

export function levelLabel(level: string): string {
  const map: Record<string, string> = {
    debutant: "Débutant",
    intermediaire: "Intermédiaire",
    avance: "Avancé",
  };
  return map[level] ?? level;
}
