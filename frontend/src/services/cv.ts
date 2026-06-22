import { api } from "@/services/api";
import { getFirebaseIdToken } from "@/lib/firebase";

export interface CVFile {
  id: number;
  original_filename: string;
  mime_type: string;
  status: string;
  extracted_text: string | null;
}

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
