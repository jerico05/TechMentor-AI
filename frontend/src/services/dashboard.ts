import type { QueryClient } from "@tanstack/react-query";

import { api } from "@/services/api";
import type {
  AnalysisResult,
  ChatSession,
  CVFile,
  DashboardSummary,
  GitHubAnalysis,
  QuizAttempt,
  Roadmap,
  StudentProfile,
} from "@/types";

export async function fetchDashboardSummary(): Promise<DashboardSummary> {
  const { data } = await api.get<DashboardSummary>("/dashboard/me");
  return data;
}

export const DASHBOARD_SUMMARY_KEY = ["dashboard", "summary"] as const;

export function invalidateDashboardSummary(queryClient: QueryClient): void {
  void queryClient.invalidateQueries({ queryKey: DASHBOARD_SUMMARY_KEY });
}

/** Hydrate individual React Query caches from the summary payload. */
export function hydrateDashboardCaches(
  data: DashboardSummary,
  setQueryData: (key: readonly unknown[], value: unknown) => void,
): void {
  setQueryData(["profile", "me"], data.profile);
  setQueryData(["analysis", "me"], data.analysis);
  setQueryData(["cv", "me"], data.cv);
  setQueryData(["github", "me"], data.github);
  setQueryData(["roadmap", "me"], data.roadmap);
  setQueryData(["mentor", "sessions"], data.mentor_sessions);
  setQueryData(["quiz", "history"], data.quiz_history);
}

export type {
  AnalysisResult,
  ChatSession,
  CVFile,
  DashboardSummary,
  GitHubAnalysis,
  QuizAttempt,
  Roadmap,
  StudentProfile,
};
