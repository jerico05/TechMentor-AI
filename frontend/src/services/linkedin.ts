import { api, apiSlow } from "@/services/api";
import type { LinkedInAnalysis } from "@/types";

export type { LinkedInAnalysis } from "@/types";

export async function analyzeLinkedIn(
  linkedinUrl?: string,
  profileText?: string,
  pdfFile?: File | null,
): Promise<LinkedInAnalysis> {
  if (pdfFile) {
    const form = new FormData();
    form.append("linkedin_url", linkedinUrl ?? "");
    if (profileText?.trim()) form.append("profile_text", profileText.trim());
    form.append("pdf_file", pdfFile);
    const { data } = await apiSlow.post<LinkedInAnalysis>("/linkedin/analyze/pdf", form);
    return data;
  }

  const { data } = await apiSlow.post<LinkedInAnalysis>("/linkedin/analyze", {
    linkedin_url: linkedinUrl ?? null,
    profile_text: profileText?.trim() || null,
  });
  return data;
}

export async function fetchLinkedInAnalysis(): Promise<LinkedInAnalysis | null> {
  const { data } = await api.get<LinkedInAnalysis | null>("/linkedin/me");
  return data;
}
