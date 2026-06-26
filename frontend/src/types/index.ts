/** API DTOs - mirror the backend Pydantic schemas. */

export interface UserPublic {
  public_id: string;
  firstname: string;
  lastname: string;
  email: string;
  email_verified: boolean;
  oauth_provider: "local" | "google" | "github";
  has_password: boolean;
}

export interface MessageResponse {
  message: string;
}

export type AcademicLevel =
  | "licence1"
  | "licence2"
  | "licence3"
  | "master1"
  | "master2"
  | "other";

export type SkillLevel = "entry" | "intermediaire" | "senior" | "debutant" | "avance";

export type ProcessingStatus = "processing" | "parsed" | "failed" | "completed" | "active" | "archived";

export interface StudentProfile {
  id: number;
  user_id: number;
  university: string | null;
  department: string | null;
  academic_level: AcademicLevel;
  career_goal: string | null;
  career_path_id: number | null;
  github_url: string | null;
  linkedin_url: string | null;
  portfolio_url: string | null;
  bio: string | null;
}

export interface StudentProfileInput {
  university?: string | null;
  department?: string | null;
  academic_level?: AcademicLevel;
  career_goal?: string | null;
  career_path_id?: number | null;
  github_url?: string | null;
  linkedin_url?: string | null;
  portfolio_url?: string | null;
  bio?: string | null;
}

export interface ApiError {
  error: {
    code: string;
    message: string;
    details?: unknown;
  };
}

export interface Skill {
  id: number;
  name: string;
  category: string;
  weight: number;
}

export interface CareerPath {
  id: number;
  slug: string;
  name: string;
  description: string | null;
  skills: Skill[];
}

export interface CVFile {
  id: number;
  original_filename: string;
  mime_type: string;
  status: ProcessingStatus | string;
  extracted_text: string | null;
}

export interface GitHubAnalysis {
  id: number;
  username: string;
  repo_count: number;
  languages: Record<string, number> | null;
  technologies: string[] | null;
  status: ProcessingStatus | string;
}

export interface LinkedInExperience {
  title?: string;
  company?: string;
  duration?: string;
  description?: string;
}

export interface LinkedInEducation {
  school?: string;
  degree?: string;
  duration?: string;
}

export interface LinkedInCertification {
  name: string;
  issuer?: string | null;
  date?: string | null;
}

export interface LinkedInAnalysis {
  id: number;
  profile_url: string;
  headline: string | null;
  summary: string | null;
  experiences: LinkedInExperience[] | null;
  education: LinkedInEducation[] | null;
  skills: string[] | null;
  certifications?: LinkedInCertification[] | null;
  total_experience_years?: number | null;
  status: ProcessingStatus | string;
}

export interface ProjectSubmission {
  id: number;
  project_title: string;
  github_url: string | null;
  description: string | null;
  status: "pending" | "approved" | "rejected";
  evaluation_score: number | null;
  feedback: string | null;
  created_at: string;
}

export interface PortfolioProject {
  id: number;
  url: string;
  title: string;
  summary: string | null;
  stack: string[] | null;
  source: string;
  status: ProcessingStatus | string;
  created_at?: string;
}

export interface PortfolioProjectsResponse {
  projects: PortfolioProject[];
  portfolio_url: string | null;
  total_completed: number;
  projects_discovered?: number;
  projects_added?: number;
}

export interface AnalysisResult {
  id: number;
  career_path_id: number;
  score: number;
  level: SkillLevel | string;
  owned_skills: string[];
  missing_skills: string[];
  created_at?: string;
  projects_completed?: number;
  experience_years?: number | null;
  level_reason?: string | null;
}

export interface RoadmapCourse {
  title: string;
  platform: string;
  url: string;
  type: "gratuit" | "payant" | "freemium" | string;
  note?: string;
}

export interface RoadmapMonth {
  month: number;
  title: string;
  skills: string[];
  actions: string[];
  courses?: RoadmapCourse[];
}

export interface RoadmapContent {
  months: RoadmapMonth[];
  summary?: string;
}

export type RoadmapDurationMonths = 3 | 6 | 12;

export interface RoadmapSuggestion {
  suggested_months: RoadmapDurationMonths;
  level: string | null;
  missing_skills_count: number;
  reason: string;
}

export interface Roadmap {
  id: number;
  career_path_id: number;
  content: RoadmapContent;
  status: ProcessingStatus | string;
  created_at?: string;
}

export interface DashboardSummary {
  profile: StudentProfile | null;
  analysis: AnalysisResult | null;
  cv: CVFile | null;
  github: GitHubAnalysis | null;
  roadmap: Roadmap | null;
  mentor_sessions: ChatSession[];
  quiz_history: QuizAttempt[];
}

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
  created_at?: string;
}

export interface QuizSubmitResponse {
  attempt: QuizAttempt;
  previous_score: number;
  new_score: number;
  new_level: SkillLevel | string;
  roadmap_id: number;
  feedback: string;
}

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
  role: "user" | "assistant" | "system" | string;
  content: string;
  created_at: string;
}

export interface ProjectDataSource {
  name: string;
  url: string;
  note?: string;
}

export interface RecommendedProject {
  title: string;
  tagline: string;
  description: string;
  track: "ai" | "ml" | "data" | "backend" | "frontend" | "fullstack" | "mobile" | "devops" | "cloud" | "security" | "qa" | "product" | "design" | "dev" | string;
  difficulty: string;
  skills_practiced: string[];
  estimated_weeks: number;
  impact?: string | null;
  stack: string[];
  data_sources: ProjectDataSource[];
  deliverables: string[];
}

export interface ProjectRecommendation {
  level: SkillLevel | string;
  score: number;
  missing_skills: string[];
  career_name: string;
  career_slug: string;
  projects: RecommendedProject[];
}
