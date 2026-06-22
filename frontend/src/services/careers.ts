import { api } from "@/services/api";
import { getFirebaseIdToken } from "@/lib/firebase";

export interface CareerPath {
  id: number;
  slug: string;
  name: string;
  description: string | null;
  skills: { id: number; name: string; category: string; weight: number }[];
}

export async function fetchCareers(): Promise<CareerPath[]> {
  const { data } = await api.get<CareerPath[]>("/careers");
  return data;
}
