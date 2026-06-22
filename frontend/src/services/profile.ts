import { api } from "@/services/api";
import type { StudentProfile, StudentProfileInput } from "@/types";

export async function fetchMyProfile(): Promise<StudentProfile | null> {
  const { data } = await api.get<StudentProfile | null>("/profiles/me");
  return data;
}

export async function upsertMyProfile(payload: StudentProfileInput): Promise<StudentProfile> {
  const { data } = await api.put<StudentProfile>("/profiles/me", payload);
  return data;
}

export function computeProfileProgress(profile: StudentProfile | null): number {
  if (!profile) return 0;
  const fields = [
    profile.university,
    profile.department,
    profile.career_goal,
    profile.github_url,
    profile.bio,
  ];
  const filled = fields.filter(Boolean).length;
  return Math.round((filled / fields.length) * 100);
}
