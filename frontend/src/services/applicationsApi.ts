import { api } from './api';
import type { Application, ApplicationStatus, JobMatchResult } from '../types';

export const applicationsApi = {
  list: async (status?: string): Promise<Application[]> => {
    const res = await api.get<{ success: boolean; data: Application[] }>('/applications', {
      params: status ? { status } : undefined,
    });
    return res.data.data!;
  },

  get: async (id: string): Promise<Application> => {
    const res = await api.get<{ success: boolean; data: Application }>(`/applications/${id}`);
    return res.data.data!;
  },

  create: async (data: { jobId: string; resumeId?: string; notes?: string }): Promise<Application> => {
    const res = await api.post<{ success: boolean; data: Application }>('/applications', data);
    return res.data.data!;
  },

  updateStatus: async (id: string, status: ApplicationStatus, notes?: string): Promise<Application> => {
    const res = await api.patch<{ success: boolean; data: Application }>(`/applications/${id}/status`, { status, notes });
    return res.data.data!;
  },

  update: async (id: string, data: { notes?: string; coverLetter?: string; resumeId?: string }): Promise<Application> => {
    const res = await api.patch<{ success: boolean; data: Application }>(`/applications/${id}`, data);
    return res.data.data!;
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(`/applications/${id}`);
  },

  generateCoverLetter: async (id: string, tone?: string): Promise<string> => {
    const res = await api.post<{ success: boolean; data: { coverLetter: string } }>(`/applications/${id}/cover-letter`, { tone });
    return res.data.data!.coverLetter;
  },

  matchResume: async (id: string): Promise<JobMatchResult> => {
    const res = await api.post<{ success: boolean; data: JobMatchResult }>(`/applications/${id}/match`);
    return res.data.data!;
  },
};
