import { api } from "@/services/api";

export interface RoadmapMonth {
  month: number;
  title: string;
  skills: string[];
  actions: string[];
}

export interface RoadmapContent {
  months: RoadmapMonth[];
  summary?: string;
}

export interface Roadmap {
  id: number;
  career_path_id: number;
  content: RoadmapContent;
  status: string;
}

export async function generateRoadmap(careerPathId?: number): Promise<Roadmap> {
  const { data } = await api.post<Roadmap>("/roadmaps/generate", {
    career_path_id: careerPathId ?? null,
  }, { timeout: 90_000 });
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
