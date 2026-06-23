"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import type { Route } from "next";
import { History, Loader2 } from "lucide-react";
import type { ReactNode } from "react";

import { Motion } from "@/components/ui/motion";
import { useAppReady } from "@/lib/use-app-ready";
import { formatDate } from "@/lib/utils";
import { fetchAnalysisHistory, levelLabel } from "@/services/analysis";
import { fetchSessions } from "@/services/mentor";
import { fetchQuizHistory } from "@/services/quiz";
import { fetchRoadmapHistory } from "@/services/roadmap";

export default function HistoryPage() {
  const appReady = useAppReady();
  const { data: analyses, isLoading: la, isError: ea } = useQuery({
    queryKey: ["analysis", "history"],
    queryFn: fetchAnalysisHistory,
    enabled: appReady,
  });
  const { data: roadmaps, isLoading: lr, isError: er } = useQuery({
    queryKey: ["roadmap", "history"],
    queryFn: fetchRoadmapHistory,
    enabled: appReady,
  });
  const { data: quizzes, isLoading: lq, isError: eq } = useQuery({
    queryKey: ["quiz", "history"],
    queryFn: fetchQuizHistory,
    enabled: appReady,
  });
  const { data: sessions, isLoading: ls, isError: es } = useQuery({
    queryKey: ["mentor", "sessions"],
    queryFn: fetchSessions,
    enabled: appReady,
  });

  const loading = la || lr || lq || ls;
  const hasError = ea || er || eq || es;

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
      ) : hasError ? (
        <div className="glass-card p-6 text-center text-sm text-destructive">
          Impossible de charger l&apos;historique. Réessayez plus tard.
        </div>
      ) : (
        <div className="space-y-6">
          <Section title="Analyses skill gap">
            {analyses?.length ? analyses.map((a) => (
              <Item
                key={a.id}
                href="/analysis"
                label={`Score ${a.score}/100 · ${levelLabel(a.level)}`}
                sub={`${a.owned_skills.length} acquises, ${a.missing_skills.length} lacunes`}
                date={a.created_at}
              />
            )) : <Empty />}
          </Section>

          <Section title="Roadmaps">
            {roadmaps?.length ? roadmaps.map((r) => (
              <Item
                key={r.id}
                href="/roadmap"
                label={r.content.summary?.slice(0, 80) ?? `Roadmap #${r.id}`}
                sub={`Statut : ${r.status}`}
                date={r.created_at}
              />
            )) : <Empty />}
          </Section>

          <Section title="Quiz">
            {quizzes?.length ? quizzes.map((q) => (
              <Item
                key={q.id}
                href="/quiz"
                label={`Score quiz ${q.score}%`}
                sub={q.feedback ?? ""}
                date={q.created_at}
              />
            )) : <Empty />}
          </Section>

          <Section title="Conversations mentor">
            {sessions?.length ? sessions.map((s) => (
              <Item
                key={s.id}
                href={`/mentor?session=${s.id}`}
                label={s.title}
                sub="Ouvrir la conversation"
                date={s.created_at}
              />
            )) : <Empty />}
          </Section>
        </div>
      )}
    </div>
  );
}

function Section({ title, children }: { title: string; children: ReactNode }) {
  return (
    <div className="glass-card p-5">
      <h2 className="mb-3 font-semibold">{title}</h2>
      <ul className="space-y-2">{children}</ul>
    </div>
  );
}

function Item({ label, sub, date, href }: { label: string; sub: string; date?: string; href?: string }) {
  const content = (
  <>
      <p className="break-words font-medium">{label}</p>
      {sub && <p className="break-words text-xs text-muted-foreground">{sub}</p>}
      {date && <p className="mt-1 text-xs text-muted-foreground">{formatDate(date)}</p>}
    </>
  );

  if (href) {
    return (
      <li>
        <Link href={href as Route} className="block min-w-0 rounded-xl bg-secondary/40 px-4 py-3 text-sm transition-colors hover:bg-secondary/60">
          {content}
        </Link>
      </li>
    );
  }

  return (
    <li className="rounded-xl bg-secondary/40 px-4 py-3 text-sm">
      {content}
    </li>
  );
}

function Empty() {
  return <p className="text-sm text-muted-foreground">Aucun élément.</p>;
}
