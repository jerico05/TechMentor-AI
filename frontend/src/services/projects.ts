import { api, apiSlow } from "@/services/api";
import type { ProjectRecommendation, ProjectSubmission } from "@/types";

export type { ProjectRecommendation, RecommendedProject, ProjectDataSource, ProjectSubmission } from "@/types";

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

export interface SubmitProjectPayload {
  project_title: string;
  career_slug?: string | null;
  project_description?: string;
  skills_practiced?: string[];
  deliverables?: string[];
  github_url?: string | null;
  user_description?: string | null;
}

export async function submitProjectProof(payload: SubmitProjectPayload): Promise<ProjectSubmission> {
  const { data } = await api.post<ProjectSubmission>("/projects/submit", payload);
  return data;
}

export async function fetchProjectSubmissions(): Promise<ProjectSubmission[]> {
  const { data } = await api.get<ProjectSubmission[]>("/projects/submissions");
  return data;
}
