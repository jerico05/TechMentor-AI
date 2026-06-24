"use client";

import Link from "next/link";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { ClipboardCheck, Loader2 } from "lucide-react";
import * as React from "react";

import { Button } from "@/components/ui/button";
import { Motion } from "@/components/ui/motion";
import { levelLabel } from "@/services/analysis";
import { invalidateDashboardSummary } from "@/services/dashboard";
import { generateQuiz, submitQuiz, type QuizQuestion, type QuizSubmitResponse } from "@/services/quiz";
import { isApiError } from "@/services/api";

export default function QuizPage() {
  const queryClient = useQueryClient();
  const [quizId, setQuizId] = React.useState<string | null>(null);
  const [questions, setQuestions] = React.useState<QuizQuestion[]>([]);
  const [answers, setAnswers] = React.useState<Record<string, number>>({});
  const [result, setResult] = React.useState<QuizSubmitResponse | null>(null);

  const generateMut = useMutation({
    mutationFn: generateQuiz,
    onSuccess: (data) => {
      setQuizId(data.quiz_id);
      setQuestions(data.questions);
      setAnswers({});
      setResult(null);
    },
  });

  const submitMut = useMutation({
    mutationFn: () => submitQuiz(quizId!, answers),
    onSuccess: (data) => {
      setResult(data);
      setQuizId(null);
      void queryClient.invalidateQueries({ queryKey: ["roadmap"] });
      void queryClient.invalidateQueries({ queryKey: ["analysis"] });
      void queryClient.invalidateQueries({ queryKey: ["quiz", "history"] });
      void queryClient.invalidateQueries({ queryKey: ["projects", "recommendations"] });
      void queryClient.invalidateQueries({ queryKey: ["roadmap", "suggestion"] });
      invalidateDashboardSummary(queryClient);
    },
  });

  return (
    <div className="mx-auto max-w-2xl">
      <Motion animation="slide-up" delay={1} className="mb-6">
        <h1 className="text-3xl font-extrabold tracking-tight text-[hsl(var(--navy))]">Évaluation</h1>
        <p className="text-muted-foreground">Testez vos connaissances et déclenchez une nouvelle roadmap.</p>
      </Motion>

      {!quizId && !result && (
        <Motion animation="scale-in" delay={2} className="glass-card p-8 text-center">
          <ClipboardCheck className="mx-auto mb-4 h-12 w-12 text-primary" />
          <Button onClick={() => generateMut.mutate()} disabled={generateMut.isPending} className="rounded-2xl">
            {generateMut.isPending ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
            Démarrer le quiz
          </Button>
          {generateMut.isError && (
            <p className="mt-4 text-sm text-destructive">
              {isApiError(generateMut.error) ? generateMut.error.error.message : "Impossible de générer le quiz."}
            </p>
          )}
        </Motion>
      )}

      {quizId && questions.length > 0 && (
        <div className="space-y-6">
          {questions.map((q, i) => (
            <div key={q.id} className="glass-card p-5">
              <p className="mb-3 font-medium">{i + 1}. {q.question}</p>
              <div className="space-y-2">
                {q.options.map((opt, idx) => (
                  <label
                    key={opt}
                    className={`flex cursor-pointer items-center gap-3 rounded-xl border px-4 py-2.5 text-sm ${
                      answers[q.id] === idx ? "border-primary bg-primary/5" : "hover:bg-secondary/50"
                    }`}
                  >
                    <input
                      type="radio"
                      name={q.id}
                      checked={answers[q.id] === idx}
                      onChange={() => setAnswers((a) => ({ ...a, [q.id]: idx }))}
                    />
                    {opt}
                  </label>
                ))}
              </div>
            </div>
          ))}
          <Button
            onClick={() => submitMut.mutate()}
            disabled={submitMut.isPending || Object.keys(answers).length < questions.length}
            className="w-full rounded-2xl"
          >
            {submitMut.isPending ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
            Soumettre
          </Button>
          {submitMut.isError && (
            <p className="text-center text-sm text-destructive">
              {isApiError(submitMut.error) ? submitMut.error.error.message : "Erreur lors de la soumission."}
            </p>
          )}
        </div>
      )}

      {result && (
        <Motion animation="scale-in" className="glass-card mt-6 space-y-4 p-8 text-center">
          <p className="text-sm text-muted-foreground">Quiz : {result.attempt.score}%</p>
          <div className="flex items-center justify-center gap-4">
            <div>
              <p className="text-xs text-muted-foreground">Avant</p>
              <p className="text-2xl font-bold">{result.previous_score}</p>
            </div>
            <span className="text-2xl text-primary">→</span>
            <div>
              <p className="text-xs text-muted-foreground">Après</p>
              <p className="text-2xl font-bold text-primary">{result.new_score}</p>
            </div>
          </div>
          <p className="font-semibold">{levelLabel(result.new_level)}</p>
          <p className="text-sm text-muted-foreground">{result.feedback}</p>
          <div className="flex flex-wrap justify-center gap-3">
            <Button asChild className="rounded-2xl">
              <Link href="/roadmap">Voir ma nouvelle roadmap</Link>
            </Button>
            <Button variant="outline" className="rounded-2xl" onClick={() => { setResult(null); generateMut.mutate(); }}>
              Nouveau quiz
            </Button>
          </div>
        </Motion>
      )}
    </div>
  );
}
