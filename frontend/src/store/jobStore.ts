import { create } from 'zustand';
import type { JobSearchFilters } from '../types';

interface JobStore {
  filters: JobSearchFilters;
  setFilters: (filters: Partial<JobSearchFilters>) => void;
  resetFilters: () => void;
}

const DEFAULT_FILTERS: JobSearchFilters = {
  keyword: '',
  location: '',
  page: 1,
  limit: 20,
};

export const useJobStore = create<JobStore>((set) => ({
  filters: DEFAULT_FILTERS,

  setFilters: (filters) =>
    set((state) => ({
      filters: { ...state.filters, ...filters, page: 1 },
    })),

  resetFilters: () => set({ filters: DEFAULT_FILTERS }),
}));
