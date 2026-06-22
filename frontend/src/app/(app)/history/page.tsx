"use client";

import { useQuery } from "@tanstack/react-query";
import { History, Loader2 } from "lucide-react";

import { Motion } from "@/components/ui/motion";
import { fetchAnalysisHistory, levelLabel } from "@/services/analysis";
import { fetchSessions } from "@/services/mentor";
import { fetchQuizHistory } from "@/services/quiz";
import { fetchRoadmapHistory } from "@/services/roadmap";

export default function HistoryPage() {
  const { data: analyses, isLoading: la } = useQuery({
    queryKey: ["analysis", "history"],
    queryFn: fetchAnalysisHistory,
  });
  const { data: roadmaps, isLoading: lr } = useQuery({
    queryKey: ["roadmap", "history"],
    queryFn: fetchRoadmapHistory,
  });
  const { data: quizzes, isLoading: lq } = useQuery({
    queryKey: ["quiz", "history"],
    queryFn: fetchQuizHistory,
  });
  const { data: sessions, isLoading: ls } = useQuery({
    queryKey: ["mentor", "sessions"],
    queryFn: fetchSessions,
  });

  const loading = la || lr || lq || ls;

  return (
    <div className="mx-auto max-w-3xl">
      <Motion animation="slide-up" delay={1} className="mb-6">
        <h1 className="flex items-center gap-2 text-3xl font-extrabold text-[hsl(var(--navy))]">
          <History className="h-8 w-8 text-primary" />
          Historique
        </h1>
        <p className="text-muted-foreground">Analyses, roadmaps, quiz et conversations mentor.</p>
      </Motion>

      {loading ? (
        <div className="flex justify-center py-16"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>
      ) : (
        <div className="space-y-6">
          <Section title="Analyses skill gap">
            {analyses?.length ? analyses.map((a) => (
              <Item key={a.id} label={`Score ${a.score}/100 — ${levelLabel(a.level)}`} sub={`${a.owned_skills.length} acquises, ${a.missing_skills.length} lacunes`} />
            )) : <Empty />}
          </Section>

          <Section title="Roadmaps">
            {roadmaps?.length ? roadmaps.map((r) => (
              <Item key={r.id} label={r.content.summary?.slice(0, 80) ?? `Roadmap #${r.id}`} sub={`Statut : ${r.status}`} />
            )) : <Empty />}
          </Section>

          <Section title="Quiz">
            {quizzes?.length ? quizzes.map((q) => (
              <Item key={q.id} label={`Score quiz ${q.score}%`} sub={q.feedback ?? ""} />
            )) : <Empty />}
          </Section>

          <Section title="Conversations mentor">
            {sessions?.length ? sessions.map((s) => (
              <Item key={s.id} label={s.title} sub={new Date(s.created_at).toLocaleString("fr-FR")} />
            )) : <Empty />}
          </Section>
        </div>
      )}
    </div>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="glass-card p-5">
      <h2 className="mb-3 font-semibold">{title}</h2>
      <ul className="space-y-2">{children}</ul>
    </div>
  );
}

function Item({ label, sub }: { label: string; sub: string }) {
  return (
    <li className="rounded-xl bg-secondary/40 px-4 py-3 text-sm">
      <p className="font-medium">{label}</p>
      {sub && <p className="text-xs text-muted-foreground">{sub}</p>}
    </li>
  );
}

function Empty() {
  return <p className="text-sm text-muted-foreground">Aucun élément.</p>;
}
