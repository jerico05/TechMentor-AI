import { api, apiSlow } from "@/services/api";
import type { ProjectRecommendation } from "@/types";

export type { ProjectRecommendation, RecommendedProject, ProjectDataSource } from "@/types";

export async function fetchProjectRecommendations(): Promise<ProjectRecommendation> {
  const { data } = await apiSlow.get<ProjectRecommendation>("/projects/recommendations");
  return data;
}

export async function fetchProjectCompletions(): Promise<string[]> {
  const { data } = await api.get<{ completed: string[] }>("/projects/completions");
  return data.completed;
}

export async function markProjectComplete(title: string, careerSlug?: string): Promise<string[]> {
  const { data } = await api.post<{ completed: string[] }>("/projects/complete", {
    title,
    career_slug: careerSlug ?? null,
  });
  return data.completed;
}

export async function unmarkProjectComplete(title: string): Promise<string[]> {
  const { data } = await api.delete<{ completed: string[] }>("/projects/complete", {
    data: { title },
  });
  return data.completed;
}
