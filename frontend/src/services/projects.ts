import { api } from "@/services/api";

export interface ProjectRecommendation {
  level: string;
  score: number;
  missing_skills: string[];
  projects: { title: string; description: string }[];
}

export async function fetchProjectRecommendations(): Promise<ProjectRecommendation> {
  const { data } = await api.get<ProjectRecommendation>("/projects/recommendations");
  return data;
}
