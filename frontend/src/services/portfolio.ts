import { api, apiSlow } from "@/services/api";
import { invalidateDashboardSummary } from "@/services/dashboard";
import type { PortfolioProject, PortfolioProjectsResponse } from "@/types";
import type { QueryClient } from "@tanstack/react-query";

export type { PortfolioProject, PortfolioProjectsResponse } from "@/types";

export async function fetchPortfolioProjects(): Promise<PortfolioProjectsResponse> {
  const { data } = await api.get<PortfolioProjectsResponse>("/portfolio/projects");
  return data;
}

export async function addPortfolioProject(url: string): Promise<PortfolioProject> {
  const { data } = await apiSlow.post<PortfolioProject>("/portfolio/projects", { url });
  return data;
}

export async function deletePortfolioProject(projectId: number): Promise<PortfolioProjectsResponse> {
  const { data } = await api.delete<PortfolioProjectsResponse>(`/portfolio/projects/${projectId}`);
  return data;
}

export async function savePortfolioUrl(portfolioUrl: string | null): Promise<PortfolioProjectsResponse> {
  const { data } = await api.put<PortfolioProjectsResponse>("/portfolio/url", {
    portfolio_url: portfolioUrl,
  });
  return data;
}

export function invalidatePortfolioQueries(queryClient: QueryClient) {
  queryClient.invalidateQueries({ queryKey: ["portfolio", "projects"] });
  queryClient.invalidateQueries({ queryKey: ["profile", "me"] });
  queryClient.invalidateQueries({ queryKey: ["analysis", "me"] });
  invalidateDashboardSummary(queryClient);
}
