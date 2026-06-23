import type { QueryClient } from "@tanstack/react-query";
import type { AppRouterInstance } from "next/dist/shared/lib/app-router-context.shared-runtime";

import { APP_ROUTES } from "@/lib/app-routes";
import { getFirebaseIdToken } from "@/lib/firebase";
import { fetchLatestAnalysis, fetchAnalysisHistory } from "@/services/analysis";
import { fetchCareers } from "@/services/careers";
import { fetchMyCV } from "@/services/cv";
import { fetchGitHubAnalysis } from "@/services/github";
import { fetchSessions } from "@/services/mentor";
import { fetchMyProfile } from "@/services/profile";
import { fetchProjectCompletions, fetchProjectRecommendations } from "@/services/projects";
import { fetchQuizHistory } from "@/services/quiz";
import { fetchActiveRoadmap, fetchRoadmapHistory, fetchRoadmapSuggestion } from "@/services/roadmap";

type RouterPrefetch = Pick<AppRouterInstance, "prefetch">;

/** Warm webpack chunks for every app page (first click feels instant). */
const APP_PAGE_IMPORTS = [
  () => import("@/app/(app)/dashboard/page"),
  () => import("@/app/(app)/analysis/page"),
  () => import("@/app/(app)/roadmap/page"),
  () => import("@/app/(app)/projects/page"),
  () => import("@/app/(app)/mentor/page"),
  () => import("@/app/(app)/quiz/page"),
  () => import("@/app/(app)/history/page"),
  () => import("@/app/(app)/settings/page"),
] as const;

const HEAVY_COMPONENT_IMPORTS = [
  () => import("@/components/roadmap/roadmap-infographic"),
  () => import("@/components/careers/career-select"),
  () => import("@/components/settings/profile-settings-panel"),
  () => import("@/components/settings/cv-settings-panel"),
  () => import("@/components/settings/github-settings-panel"),
] as const;

export function prefetchAppRoutes(router: RouterPrefetch): void {
  APP_ROUTES.forEach((href) => router.prefetch(href));
}

export async function prefetchAppPageChunks(): Promise<void> {
  await Promise.allSettled([
    ...APP_PAGE_IMPORTS.map((load) => load()),
    ...HEAVY_COMPONENT_IMPORTS.map((load) => load()),
  ]);
}

export async function prefetchAppData(queryClient: QueryClient): Promise<void> {
  void getFirebaseIdToken();

  const queries = [
    { queryKey: ["profile", "me"] as const, queryFn: fetchMyProfile },
    { queryKey: ["careers"] as const, queryFn: fetchCareers, staleTime: 10 * 60 * 1000 },
    { queryKey: ["analysis", "me"] as const, queryFn: fetchLatestAnalysis },
    { queryKey: ["analysis", "history"] as const, queryFn: fetchAnalysisHistory },
    { queryKey: ["cv", "me"] as const, queryFn: fetchMyCV },
    { queryKey: ["github", "me"] as const, queryFn: fetchGitHubAnalysis },
    { queryKey: ["roadmap", "me"] as const, queryFn: fetchActiveRoadmap },
    { queryKey: ["roadmap", "suggestion"] as const, queryFn: fetchRoadmapSuggestion },
    { queryKey: ["roadmap", "history"] as const, queryFn: fetchRoadmapHistory },
    { queryKey: ["mentor", "sessions"] as const, queryFn: fetchSessions },
    { queryKey: ["quiz", "history"] as const, queryFn: fetchQuizHistory },
    {
      queryKey: ["projects", "recommendations"] as const,
      queryFn: fetchProjectRecommendations,
      staleTime: 15 * 60 * 1000,
    },
    { queryKey: ["projects", "completions"] as const, queryFn: fetchProjectCompletions },
  ];

  await Promise.allSettled(
    queries.map((q) =>
      queryClient.prefetchQuery({
        queryKey: q.queryKey,
        queryFn: q.queryFn as () => Promise<unknown>,
        staleTime: q.staleTime ?? 60 * 1000,
      }),
    ),
  );
}

export function runAppPrefetch(router: RouterPrefetch, queryClient: QueryClient): void {
  prefetchAppRoutes(router);
  void prefetchAppPageChunks();
  void prefetchAppData(queryClient);
}
