/** API DTOs — mirror the backend Pydantic schemas. */

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

export interface StudentProfile {
  id: number;
  user_id: number;
  university: string | null;
  department: string | null;
  academic_level: AcademicLevel;
  career_goal: string | null;
  career_path_id: number | null;
  github_url: string | null;
  bio: string | null;
}

export interface StudentProfileInput {
  university?: string | null;
  department?: string | null;
  academic_level?: AcademicLevel;
  career_goal?: string | null;
  career_path_id?: number | null;
  github_url?: string | null;
  bio?: string | null;
}

export interface ApiError {
  error: {
    code: string;
    message: string;
    details?: unknown;
  };
}
