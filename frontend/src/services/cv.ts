import { api } from "@/services/api";
import { getFirebaseIdToken } from "@/lib/firebase";
import type { CVFile } from "@/types";

export type { CVFile } from "@/types";

export async function fetchMyCV(): Promise<CVFile | null> {
  const { data } = await api.get<CVFile | null>("/cv/me");
  return data;
}

export async function uploadCV(file: File): Promise<CVFile> {
  const form = new FormData();
  form.append("file", file);
  const token = await getFirebaseIdToken();
  const { data } = await api.post<CVFile>("/cv/upload", form, {
    headers: {
      "Content-Type": "multipart/form-data",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    timeout: 120_000,
  });
  return data;
}
