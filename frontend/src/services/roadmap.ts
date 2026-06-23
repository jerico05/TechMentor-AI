import { api } from "@/services/api";
import type { Roadmap, RoadmapContent, RoadmapDurationMonths, RoadmapMonth, RoadmapSuggestion } from "@/types";

export type { Roadmap, RoadmapContent, RoadmapDurationMonths, RoadmapMonth, RoadmapSuggestion } from "@/types";

export async function fetchRoadmapSuggestion(): Promise<RoadmapSuggestion> {
  const { data } = await api.get<RoadmapSuggestion>("/roadmaps/suggestion");
  return data;
}

export async function generateRoadmap(
  options?: { careerPathId?: number; durationMonths?: RoadmapDurationMonths },
): Promise<Roadmap> {
  const { data } = await api.post<Roadmap>(
    "/roadmaps/generate",
    {
      career_path_id: options?.careerPathId ?? null,
      duration_months: options?.durationMonths ?? null,
    },
    { timeout: 120_000 },
  );
  return data;
}

export async function fetchActiveRoadmap(): Promise<Roadmap | null> {
  const { data } = await api.get<Roadmap | null>("/roadmaps/me");
  return data;
}

export async function fetchRoadmapHistory(): Promise<Roadmap[]> {
  const { data } = await api.get<Roadmap[]>("/roadmaps/history");
  return data;
}
