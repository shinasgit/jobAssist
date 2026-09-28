import { api } from './api';
import type { UserSettings } from '../types';

export const settingsApi = {
  get: async (): Promise<UserSettings> => {
    const res = await api.get<UserSettings>('/settings');
    return res.data;
  },

  update: async (data: Partial<UserSettings>): Promise<UserSettings> => {
    const res = await api.put<UserSettings>('/settings', data);
    return res.data;
  },
};
