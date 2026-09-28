import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Search, MapPin, Filter, Briefcase } from 'lucide-react';
import { jobsApi } from '../services/jobsApi';
import { useJobStore } from '../store/jobStore';
import type { RemoteType } from '../types';
import clsx from 'clsx';
import { JobCard } from '../components/jobs/JobCard';

const REMOTE_OPTIONS: { value: RemoteType; label: string }[] = [
  { value: 'remote', label: 'Remote' },
  { value: 'hybrid', label: 'Hybrid' },
  { value: 'onsite', label: 'On-site' },
];

export default function Jobs() {
  const { filters, setFilters, resetFilters } = useJobStore();
  const [localKeyword, setLocalKeyword] = useState(filters.keyword ?? '');
  const [showFilters, setShowFilters] = useState(false);

  const { data, isLoading, isFetching } = useQuery({
    queryKey: ['jobs', filters],
    queryFn: () => jobsApi.list(filters),
  });

  function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    setFilters({ keyword: localKeyword, page: 1 });
  }

  function toggleRemote(value: RemoteType) {
    const current = filters.remoteType ?? [];
    const next = current.includes(value)
      ? current.filter((v) => v !== value)
      : [...current, value];
    setFilters({ remoteType: next });
  }

  return (
    <div className="max-w-5xl mx-auto space-y-6 w-full min-w-0">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <div>
          <h1 className="text-xl sm:text-2xl lg:text-3xl font-bold tracking-tight text-surface-50">Job Search</h1>
          <p className="text-xs sm:text-sm text-surface-400 mt-1">
            {data ? `${data.total.toLocaleString()} jobs found` : 'Searching…'}
          </p>
        </div>
      </div>

      {/* Search Bar */}
      <form id="form-job-search" onSubmit={handleSearch} className="flex flex-col sm:flex-row gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-surface-500" />
          <input
            id="input-job-keyword"
            type="text"
            placeholder="Job title, company, or skill…"
            value={localKeyword}
            onChange={(e) => setLocalKeyword(e.target.value)}
            className="input pl-10 w-full"
          />
        </div>
        <div className="relative w-full sm:w-48">
          <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-surface-500" />
          <input
            id="input-job-location"
            type="text"
            placeholder="Location"
            value={filters.location ?? ''}
            onChange={(e) => setFilters({ location: e.target.value })}
            className="input pl-10 w-full"
          />
        </div>
        <div className="flex gap-2">
          <button type="submit" id="btn-search" className="btn-primary flex-1 sm:flex-initial px-5 justify-center">
            Search
          </button>
          <button
            type="button"
            id="btn-toggle-filters"
            onClick={() => setShowFilters((s) => !s)}
            className="btn-secondary"
          >
            <Filter className="w-4 h-4" />
          </button>
        </div>
      </form>

      {/* Filters Panel */}
      {showFilters && (
        <div className="glass-card p-4 space-y-4 animate-slide-up">
          <div>
            <p className="text-xs font-semibold text-surface-400 uppercase tracking-wider mb-2">Work Mode</p>
            <div className="flex flex-wrap gap-2">
              {REMOTE_OPTIONS.map(({ value, label }) => (
                <button
                  key={value}
                  id={`filter-remote-${value}`}
                  type="button"
                  onClick={() => toggleRemote(value)}
                  className={clsx('badge cursor-pointer transition-all', {
                    'badge-success': filters.remoteType?.includes(value),
                    'badge-neutral': !filters.remoteType?.includes(value),
                  })}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>

          <div className="flex justify-end">
            <button id="btn-reset-filters" type="button" onClick={resetFilters} className="btn-ghost btn-sm">
              Reset filters
            </button>
          </div>
        </div>
      )}

      {/* Results */}
      <div className="space-y-3 relative">
        {isFetching && !isLoading && (
          <div className="absolute top-0 right-0">
            <div className="w-4 h-4 border-2 border-brand-500/30 border-t-brand-500 rounded-full animate-spin" />
          </div>
        )}

        {isLoading ? (
          Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="glass-card p-4 sm:p-5 space-y-3">
              <div className="flex gap-4">
                <div className="skeleton w-12 h-12 rounded-xl" />
                <div className="flex-1 space-y-2">
                  <div className="skeleton h-4 w-48" />
                  <div className="skeleton h-3 w-32" />
                  <div className="flex gap-2 mt-2">
                    <div className="skeleton h-5 w-16 rounded-full" />
                    <div className="skeleton h-5 w-16 rounded-full" />
                  </div>
                </div>
              </div>
            </div>
          ))
        ) : data?.items?.length === 0 ? (
          <div className="glass-card p-8 sm:p-12 text-center flex flex-col items-center justify-center">
            <Briefcase className="w-12 h-12 text-surface-600 mb-4" />
            <p className="text-surface-300 font-medium">No jobs found</p>
            <p className="text-surface-500 text-sm mt-1">Try different keywords or filters</p>
            <button id="btn-reset-search" onClick={resetFilters} className="btn-secondary btn-sm mt-4">
              Clear filters
            </button>
          </div>
        ) : (
          data?.items?.map((job) => <JobCard key={job.id} job={job} />)
        )}
      </div>

      {/* Pagination */}
      {data && Math.ceil(data.total / data.limit) > 1 && (
        <div className="flex items-center justify-center gap-2 pt-2">
          <button
            id="btn-prev-page"
            disabled={filters.page === 1}
            onClick={() => setFilters({ page: (filters.page ?? 1) - 1 })}
            className="btn-secondary btn-sm disabled:opacity-40"
          >
            Previous
          </button>
          <span className="text-xs sm:text-sm text-surface-400 px-2">
            Page {filters.page ?? 1} of {Math.ceil(data.total / data.limit)}
          </span>
          <button
            id="btn-next-page"
            disabled={(filters.page ?? 1) >= Math.ceil(data.total / data.limit)}
            onClick={() => setFilters({ page: (filters.page ?? 1) + 1 })}
            className="btn-secondary btn-sm disabled:opacity-40"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}
