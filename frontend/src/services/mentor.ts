import { API_BASE_URL } from "@/lib/constants";
import { getFirebaseIdToken } from "@/lib/firebase";
import { api, isApiError } from "@/services/api";
import type {
  ChatMessage,
  ChatMessageRecord,
  ChatSession,
  MentorChatResponse,
} from "@/types";

export type { ChatMessage, ChatMessageRecord, ChatSession, MentorChatResponse } from "@/types";

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

async function parseStreamError(res: Response): Promise<string> {
  try {
    const text = await res.text();
    const payload = JSON.parse(text) as { error?: { message?: string } };
    if (payload.error?.message) return payload.error.message;
    return text.slice(0, 200) || `Erreur serveur (${res.status}).`;
  } catch {
    return `Erreur serveur (${res.status}).`;
  }
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
      Accept: "text/event-stream",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify({
      message,
      history: history.map((m) => ({ role: m.role, content: m.content })),
      session_id: sessionId ?? null,
    }),
  });
  if (!res.ok || !res.body) {
    throw new Error(await parseStreamError(res));
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
        error?: string;
      };
      if (payload.error) throw new Error(payload.error);
      if (payload.token) onToken(payload.token);
      if (payload.done) {
        finalSessionId = payload.session_id ?? finalSessionId;
        finalReply = payload.reply ?? finalReply;
      }
    }
  }

  if (!finalReply.trim()) {
    throw new Error("Réponse vide du mentor.");
  }

  return { sessionId: finalSessionId, reply: finalReply };
}

/** Try SSE stream first; fall back to standard POST if streaming fails. */
export async function sendMentorMessageWithFallback(
  message: string,
  history: ChatMessage[],
  sessionId: number | null | undefined,
  onToken?: (token: string) => void,
): Promise<{ sessionId: number | null; reply: string }> {
  try {
    return await streamMentorMessage(message, history, sessionId, onToken ?? (() => undefined));
  } catch {
    const result = await sendMentorMessage(message, history, sessionId);
    return { sessionId: result.session_id ?? sessionId ?? null, reply: result.reply };
  }
}

export async function fetchSessions(): Promise<ChatSession[]> {
  const { data } = await api.get<ChatSession[]>("/mentor/sessions");
  return data;
}

export async function fetchSessionMessages(sessionId: number): Promise<ChatMessageRecord[]> {
  const { data } = await api.get<ChatMessageRecord[]>(`/mentor/sessions/${sessionId}/messages`);
  return data;
}

export { isApiError };
