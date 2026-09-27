import { api } from './api';
import type { Job, PaginatedResponse, JobSearchFilters } from '../types';

type JobWithSaved = Job & { isSaved?: boolean };

export const jobsApi = {
  list: async (filters?: JobSearchFilters): Promise<PaginatedResponse<JobWithSaved>> => {
    const res = await api.get<JobWithSaved[]>('/jobs', {
      params: {
        ...filters,
        remote_type: filters?.remoteType?.join(','),
        employment_type: filters?.employmentType?.join(','),
      },
    });
    // The backend returns an array of jobs, but the frontend expects a PaginatedResponse.
    // We wrap the array into the expected format.
    return {
      items: res.data,
      total: res.data.length,
      page: filters?.page ?? 1,
      limit: filters?.limit ?? 20,
    };
  },

  get: async (id: number | string): Promise<JobWithSaved> => {
    const res = await api.get<JobWithSaved>(`/jobs/${id}`);
    return res.data;
  },

  save: async (id: number | string): Promise<void> => {
    await api.post(`/saved-jobs/${id}`);
  },

  unsave: async (id: number | string): Promise<void> => {
    await api.delete(`/saved-jobs/${id}`);
  },

  getSaved: async (): Promise<PaginatedResponse<JobWithSaved>> => {
    const res = await api.get<any[]>('/saved-jobs');
    // Transform SavedJobResponse [{ job: Job }] into JobWithSaved[]
    const items = res.data.map(item => ({
      ...item.job,
      isSaved: true,
      saved_at: item.saved_at
    }));
    return {
      items,
      total: items.length,
      page: 1,
      limit: 100,
    };
  },

  analyze: async (id: number | string): Promise<Record<string, unknown>> => {
    const res = await api.get<{ success: boolean; data: { analysis: Record<string, unknown> } }>(`/jobs/${id}/analyze`);
    return res.data.data!.analysis;
  },

  search: async (params: { keyword: string; location: string; experience: string; remote_type?: string }): Promise<any> => {
    const res = await api.post('/jobs/search', params);
    return res.data;
  }
};
