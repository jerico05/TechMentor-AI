import { api } from "@/services/api";

export interface GitHubAnalysis {
  id: number;
  username: string;
  repo_count: number;
  languages: Record<string, number> | null;
  technologies: string[] | null;
  status: string;
}

export async function analyzeGitHub(githubUrl?: string): Promise<GitHubAnalysis> {
  const { data } = await api.post<GitHubAnalysis>("/github/analyze", {
    github_url: githubUrl ?? null,
  });
  return data;
}

export async function fetchGitHubAnalysis(): Promise<GitHubAnalysis | null> {
  const { data } = await api.get<GitHubAnalysis | null>("/github/me");
  return data;
}
