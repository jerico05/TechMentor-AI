import { api } from "@/services/api";
import type { QuizAttempt, QuizGenerateResponse, QuizQuestion, QuizSubmitResponse } from "@/types";

export type { QuizAttempt, QuizGenerateResponse, QuizQuestion, QuizSubmitResponse } from "@/types";

export async function generateQuiz(): Promise<QuizGenerateResponse> {
  const { data } = await api.post<QuizGenerateResponse>("/quiz/generate", {}, { timeout: 90_000 });
  return data;
}

export async function submitQuiz(quizId: string, answers: Record<string, number>): Promise<QuizSubmitResponse> {
  const { data } = await api.post<QuizSubmitResponse>("/quiz/submit", { quiz_id: quizId, answers });
  return data;
}

export async function fetchQuizHistory(): Promise<QuizAttempt[]> {
  const { data } = await api.get<QuizAttempt[]>("/quiz/history");
  return data;
}
