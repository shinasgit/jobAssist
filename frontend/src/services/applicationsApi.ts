import { api } from './api';
import type { Application, ApplicationStatus } from '../types';

export const applicationsApi = {
  list: async (): Promise<Application[]> => {
    const res = await api.get<Application[]>('/applications');
    return res.data;
  },

  get: async (jobId: number | string): Promise<Application> => {
    const res = await api.get<Application>(`/applications/${jobId}`);
    return res.data;
  },

  create: async (jobId: number | string, notes?: string): Promise<Application> => {
    const res = await api.post<Application>(`/applications/${jobId}`, { notes });
    return res.data;
  },

  update: async (jobId: number | string, data: { status?: ApplicationStatus; notes?: string }): Promise<Application> => {
    const res = await api.patch<Application>(`/applications/${jobId}`, data);
    return res.data;
  },

  delete: async (jobId: number | string): Promise<void> => {
    await api.delete(`/applications/${jobId}`);
  },
};
