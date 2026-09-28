import { api } from './api';
import type { DashboardSummary } from '../types';

export const dashboardApi = {
  getSummary: async (): Promise<DashboardSummary> => {
    const res = await api.get<DashboardSummary>('/dashboard');
    return res.data;
  },
};
