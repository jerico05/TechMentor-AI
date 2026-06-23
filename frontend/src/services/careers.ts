import { api } from "@/services/api";
import type { CareerPath } from "@/types";

export type { CareerPath } from "@/types";

export async function fetchCareers(): Promise<CareerPath[]> {
  const { data } = await api.get<CareerPath[]>("/careers", {
    headers: { "Cache-Control": "no-cache", Pragma: "no-cache" },
  });
  return data;
}
