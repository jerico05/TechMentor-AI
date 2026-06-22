import { api } from "@/services/api";

export interface QuizQuestion {
  id: string;
  question: string;
  options: string[];
}

export interface QuizGenerateResponse {
  quiz_id: string;
  questions: QuizQuestion[];
}

export interface QuizAttempt {
  id: number;
  score: number;
  total_questions: number;
  feedback: string | null;
}

export interface QuizSubmitResponse {
  attempt: QuizAttempt;
  previous_score: number;
  new_score: number;
  new_level: string;
  roadmap_id: number;
  feedback: string;
}

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
