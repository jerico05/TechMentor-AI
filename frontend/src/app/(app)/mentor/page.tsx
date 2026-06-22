"use client";

import { useQuery } from "@tanstack/react-query";
import * as React from "react";
import { BrainCircuit, Loader2, MessageSquare, Plus, Send, Sparkles } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Motion } from "@/components/ui/motion";
import { formatAuthError } from "@/services/auth";
import {
  fetchSessionMessages,
  fetchSessions,
  streamMentorMessage,
  type ChatMessage,
} from "@/services/mentor";
import { isApiError } from "@/services/api";

const SUGGESTIONS = [
  "Quelles compétences dois-je acquérir pour devenir développeur fullstack ?",
  "Comment structurer mon apprentissage sur 3 mois ?",
  "Quels projets mettre en avant sur mon GitHub ?",
];

export default function MentorPage() {
  const [messages, setMessages] = React.useState<ChatMessage[]>([]);
  const [input, setInput] = React.useState("");
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [sessionId, setSessionId] = React.useState<number | null>(null);
  const [streamingText, setStreamingText] = React.useState("");
  const bottomRef = React.useRef<HTMLDivElement>(null);

  const { data: sessions, refetch: refetchSessions } = useQuery({
    queryKey: ["mentor", "sessions"],
    queryFn: fetchSessions,
  });

  React.useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading, streamingText]);

  async function loadSession(id: number) {
    setError(null);
    setSessionId(id);
    const records = await fetchSessionMessages(id);
    setMessages(
      records
        .filter((m) => m.role === "user" || m.role === "assistant")
        .map((m) => ({ role: m.role as "user" | "assistant", content: m.content })),
    );
  }

  function newSession() {
    setSessionId(null);
    setMessages([]);
    setStreamingText("");
    setError(null);
  }

  async function send(text: string) {
    if (!text.trim() || loading) return;
    setError(null);
    const userMsg: ChatMessage = { role: "user", content: text.trim() };
    const history = [...messages, userMsg];
    setMessages(history);
    setInput("");
    setLoading(true);
    setStreamingText("");

    try {
      const result = await streamMentorMessage(text.trim(), messages, sessionId, (token) => {
        setStreamingText((prev) => prev + token);
      });
      if (result.sessionId) setSessionId(result.sessionId);
      setMessages((prev) => [...prev, { role: "assistant", content: result.reply }]);
      setStreamingText("");
      refetchSessions();
    } catch (err) {
      const msg = isApiError(err)
        ? err.error.message
        : formatAuthError(err, "Le mentor est indisponible. Vérifiez que le backend tourne sur le port 8001.");
      setError(msg);
      setMessages((prev) => prev.slice(0, -1));
      setStreamingText("");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex h-[calc(100vh-8rem)] gap-4">
      <aside className="glass-card hidden w-56 shrink-0 flex-col overflow-hidden md:flex">
        <div className="flex items-center justify-between border-b border-white/50 p-3">
          <span className="text-sm font-semibold">Conversations</span>
          <button type="button" onClick={newSession} className="rounded-lg p-1 hover:bg-white/60" title="Nouvelle">
            <Plus className="h-4 w-4" />
          </button>
        </div>
        <ul className="scrollbar-thin flex-1 overflow-y-auto p-2">
          {sessions?.map((s) => (
            <li key={s.id}>
              <button
                type="button"
                onClick={() => loadSession(s.id)}
                className={`flex w-full items-center gap-2 rounded-xl px-2 py-2 text-left text-xs transition-colors ${
                  sessionId === s.id ? "bg-primary/10 text-primary" : "hover:bg-white/60"
                }`}
              >
                <MessageSquare className="h-3.5 w-3.5 shrink-0" />
                <span className="truncate">{s.title}</span>
              </button>
            </li>
          ))}
        </ul>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        <Motion animation="slide-up" delay={1} className="mb-4">
          <div className="flex items-center gap-3">
            <span className="flex h-10 w-10 items-center justify-center rounded-2xl bg-gradient-to-br from-primary to-accent text-white shadow-lg">
              <BrainCircuit className="h-5 w-5" />
            </span>
            <div>
              <h1 className="text-2xl font-extrabold tracking-tight text-[hsl(var(--navy))]">Mentor IA</h1>
              <p className="flex items-center gap-1 text-sm text-muted-foreground">
                <Sparkles className="h-3.5 w-3.5 text-accent" />
                Streaming + RAG — contexte personnalisé
              </p>
            </div>
          </div>
        </Motion>

        <div className="glass-card flex min-h-0 flex-1 flex-col overflow-hidden">
          <div className="scrollbar-thin flex-1 space-y-4 overflow-y-auto p-6">
            {messages.length === 0 && !streamingText && (
              <div className="space-y-4">
                <p className="text-sm text-muted-foreground">
                  Posez une question ou choisissez une suggestion :
                </p>
                <div className="flex flex-wrap gap-2">
                  {SUGGESTIONS.map((s) => (
                    <button
                      key={s}
                      type="button"
                      onClick={() => send(s)}
                      disabled={loading}
                      className="rounded-2xl border bg-white/90 px-4 py-2 text-left text-sm hover:bg-primary/5"
                    >
                      {s}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {messages.map((m, i) => (
              <div key={i} className={`chat-bubble-in flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
                <div
                  className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm ${
                    m.role === "user" ? "bg-primary text-white" : "bg-white/90 ring-1 ring-border/50"
                  }`}
                >
                  <p className="whitespace-pre-wrap">{m.content}</p>
                </div>
              </div>
            ))}

            {streamingText && (
              <div className="flex justify-start">
                <div className="max-w-[85%] rounded-2xl bg-white/90 px-4 py-3 text-sm ring-1 ring-border/50">
                  <p className="whitespace-pre-wrap">{streamingText}</p>
                </div>
              </div>
            )}

            {loading && !streamingText && (
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Loader2 className="h-4 w-4 animate-spin text-primary" />
                Le mentor réfléchit…
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          {error && (
            <div className="border-t bg-destructive/10 px-6 py-3 text-sm text-destructive">{error}</div>
          )}

          <form
            onSubmit={(e) => {
              e.preventDefault();
              send(input);
            }}
            className="flex gap-3 border-t bg-white/40 p-4"
          >
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Posez votre question…"
              disabled={loading}
              className="input-modern flex-1 !rounded-full"
            />
            <Button type="submit" disabled={loading || !input.trim()} size="icon" className="rounded-2xl">
              <Send className="h-4 w-4" />
            </Button>
          </form>
        </div>
      </div>
    </div>
  );
}
