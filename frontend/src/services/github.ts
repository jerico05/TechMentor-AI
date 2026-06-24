import { api, apiSlow } from "@/services/api";
import type { GitHubAnalysis } from "@/types";

export type { GitHubAnalysis } from "@/types";

export async function analyzeGitHub(githubUrl?: string): Promise<GitHubAnalysis> {
  const { data } = await apiSlow.post<GitHubAnalysis>(
    "/github/analyze",
    { github_url: githubUrl ?? null },
  );
  return data;
}

export async function fetchGitHubAnalysis(): Promise<GitHubAnalysis | null> {
  const { data } = await api.get<GitHubAnalysis | null>("/github/me");
  return data;
}
