import { api } from './api';
import type { Resume } from '../types';

export const resumeApi = {
  list: async (): Promise<Resume[]> => {
    const res = await api.get<{ success: boolean; data: Resume[] }>('/resume');
    return res.data.data!;
  },

  get: async (id: string): Promise<Resume> => {
    const res = await api.get<{ success: boolean; data: Resume }>(`/resume/${id}`);
    return res.data.data!;
  },

  upload: async (file: File): Promise<Resume> => {
    const formData = new FormData();
    formData.append('resume', file);
    const res = await api.post<{ success: boolean; data: Resume }>('/resume', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data.data!;
  },

  setDefault: async (id: string): Promise<void> => {
    await api.patch(`/resume/${id}/default`);
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(`/resume/${id}`);
  },

  extractSkills: async (id: string): Promise<Record<string, string[]>> => {
    const res = await api.post<{ success: boolean; data: Record<string, string[]> }>(`/resume/${id}/extract-skills`);
    return res.data.data!;
  },
};
