export interface User {
  id: string;
  email: string;
  name: string;
  avatar?: string;
}

export interface AuthTokenPayload {
  userId: string;
  email: string;
  exp: number;
}

export interface LoginRequest {
  email: string;
  password?: string;
}

export interface RegisterRequest {
  name: string;
  email: string;
  password?: string;
}

export interface AuthResponse {
  user: User;
  token: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
}

export interface DashboardStats {
  jobsFoundToday: number;
  relevantJobs: number;
  savedJobs: number;
  applicationsReady: number;
}

export type RemoteType = 'remote' | 'hybrid' | 'onsite';
export type EmploymentType = 'full-time' | 'part-time' | 'contract' | 'freelance' | 'internship';

export interface Job {
  id: number;
  title: string;
  company: string | null;
  location: string | null;
  remote_type: string | null;
  salary: string | null;
  experience: string | null;
  employment_type: string | null;
  description: string | null;
  source: string | null;
  source_url: string | null;
  posted_date: string | null;
  discovered_at: string;
}

export interface JobSearchFilters {
  keyword?: string;
  location?: string;
  remoteType?: RemoteType[];
  employmentType?: EmploymentType[];
  skills?: string[];
  page?: number;
  limit?: number;
}

export type ApplicationStatus = 
  | 'SAVED'
  | 'PREPARING'
  | 'READY_TO_APPLY'
  | 'USER_REVIEW'
  | 'APPLIED'
  | 'INTERVIEW'
  | 'OFFER'
  | 'REJECTED'
  | 'WITHDRAWN';

export interface Application {
  id: string;
  jobId: string;
  jobTitle: string;
  companyName: string;
  resumeId?: string;
  coverLetter?: string;
  applicationUrl?: string;
  status: ApplicationStatus;
  notes?: string;
  createdAt: string;
  updatedAt: string;
  job?: Job;
}

export interface ApplicationEvent {
  id: string;
  applicationId: string;
  eventType: string;
  description?: string;
  createdAt: string;
}

export interface JobMatchResult {
  jobId: string;
  resumeId: string;
  score: number;
  matchedSkills: string[];
  missingSkills: string[];
  experienceMatch: string;
  educationMatch: string;
  concerns: string[];
  questionsToVerify: string[];
  overallRecommendation: string;
}

export interface Resume {
  id: string;
  userId: string;
  filename: string;
  url: string;
  parsedData?: ParsedResume;
  isDefault: boolean;
  createdAt: string;
}

export interface ParsedResume {
  name?: string;
  contact?: {
    email?: string;
    phone?: string;
    location?: string;
    linkedin?: string;
    github?: string;
  };
  summary?: string;
  skills: string[];
  education: ResumeEducation[];
  experience: ResumeExperience[];
  projects: ResumeProject[];
  certifications: ResumeCertification[];
}

export interface ResumeEducation {
  degree: string;
  institution: string;
  year?: string;
}

export interface ResumeExperience {
  role: string;
  company: string;
  duration?: string;
  description: string[];
}

export interface ResumeProject {
  name: string;
  description: string;
  technologies: string[];
  url?: string;
}

export interface ResumeCertification {
  name: string;
  issuer: string;
  year?: string;
}

export interface ExtractedSkills {
  skills: string[];
}

export interface CoverLetterRequest {
  jobId: string;
  resumeId: string;
  tone?: string;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}
