import { API_BASE_URL } from "@/lib/constants";
import { getFirebaseIdToken } from "@/lib/firebase";
import { api } from "@/services/api";

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface MentorChatResponse {
  reply: string;
  model: string;
  session_id?: number | null;
}

export interface ChatSession {
  id: number;
  title: string;
  created_at: string;
}

export interface ChatMessageRecord {
  id: number;
  role: string;
  content: string;
  created_at: string;
}

export async function sendMentorMessage(
  message: string,
  history: ChatMessage[],
  sessionId?: number | null,
): Promise<MentorChatResponse> {
  const { data } = await api.post<MentorChatResponse>(
    "/mentor/chat",
    {
      message,
      history: history.map((m) => ({ role: m.role, content: m.content })),
      session_id: sessionId ?? null,
    },
    { timeout: 90_000 },
  );
  return data;
}

export async function streamMentorMessage(
  message: string,
  history: ChatMessage[],
  sessionId: number | null | undefined,
  onToken: (token: string) => void,
): Promise<{ sessionId: number | null; reply: string }> {
  const token = await getFirebaseIdToken();
  const res = await fetch(`${API_BASE_URL}/api/v1/mentor/chat/stream`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify({
      message,
      history: history.map((m) => ({ role: m.role, content: m.content })),
      session_id: sessionId ?? null,
    }),
  });
  if (!res.ok || !res.body) {
    throw new Error("Erreur de streaming mentor.");
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let finalSessionId: number | null = sessionId ?? null;
  let finalReply = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n\n");
    buffer = lines.pop() ?? "";
    for (const line of lines) {
      if (!line.startsWith("data: ")) continue;
      const payload = JSON.parse(line.slice(6)) as {
        token?: string;
        done?: boolean;
        session_id?: number;
        reply?: string;
      };
      if (payload.token) onToken(payload.token);
      if (payload.done) {
        finalSessionId = payload.session_id ?? finalSessionId;
        finalReply = payload.reply ?? finalReply;
      }
    }
  }
  return { sessionId: finalSessionId, reply: finalReply };
}

export async function fetchSessions(): Promise<ChatSession[]> {
  const { data } = await api.get<ChatSession[]>("/mentor/sessions");
  return data;
}

export async function fetchSessionMessages(sessionId: number): Promise<ChatMessageRecord[]> {
  const { data } = await api.get<ChatMessageRecord[]>(`/mentor/sessions/${sessionId}/messages`);
  return data;
}
