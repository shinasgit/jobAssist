import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Search, MapPin, Filter, Briefcase, ArrowRight, Bookmark, BookmarkCheck, Wifi, WifiOff } from 'lucide-react';
import { Link } from 'react-router-dom';
import { jobsApi } from '../services/jobsApi';
import { useJobStore } from '../store/jobStore';
import type { Job, RemoteType } from '../types';
import { format } from 'date-fns';
import toast from 'react-hot-toast';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import clsx from 'clsx';

const REMOTE_OPTIONS: { value: RemoteType; label: string }[] = [
  { value: 'remote', label: 'Remote' },
  { value: 'hybrid', label: 'Hybrid' },
  { value: 'onsite', label: 'On-site' },
];

function JobCard({ job }: { job: Job & { isSaved?: boolean } }) {
  const qc = useQueryClient();

  const { mutate: toggleSave, isPending } = useMutation({
    mutationFn: async () => {
      if (job.isSaved) await jobsApi.unsave(job.id);
      else await jobsApi.save(job.id);
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['jobs'] });
      toast.success(job.isSaved ? 'Job removed' : 'Job saved!');
    },
  });

  return (
    <div className="glass-card p-5 flex gap-4 group animate-slide-up">
      {/* Logo */}
      <div className="w-12 h-12 rounded-xl bg-gradient-brand flex items-center justify-center text-sm font-bold text-white shrink-0">
        {job.company ? job.company.charAt(0).toUpperCase() : '?'}
      </div>

      <div className="flex-1 min-w-0">
        <div className="flex items-start justify-between gap-2">
          <div>
            <Link
              id={`job-title-${job.id}`}
              to={`/jobs/${job.id}`}
              className="text-sm font-semibold text-surface-100 hover:text-brand-300 transition-colors line-clamp-1"
            >
              {job.title}
            </Link>
            <p className="text-xs text-surface-400 mt-0.5">
              {job.company ?? 'Unknown Company'}
              {job.location && ` · ${job.location}`}
            </p>
          </div>

          <button
            id={`btn-save-${job.id}`}
            onClick={(e) => { e.preventDefault(); toggleSave(); }}
            disabled={isPending}
            className="shrink-0 p-1.5 rounded-lg text-surface-500 hover:text-yellow-400 hover:bg-yellow-400/10 transition-all duration-150"
          >
            {job.isSaved
              ? <BookmarkCheck className="w-4 h-4 text-yellow-400" />
              : <Bookmark className="w-4 h-4" />}
          </button>
        </div>

        {/* Tags */}
        <div className="flex flex-wrap gap-1.5 mt-2.5">
          {job.remote_type && (
            <span className={clsx('badge text-xs', {
              'badge-success': job.remote_type.toLowerCase() === 'remote',
              'badge-brand': job.remote_type.toLowerCase() === 'hybrid',
              'badge-neutral': job.remote_type.toLowerCase() === 'onsite',
            })}>
              {job.remote_type.toLowerCase() === 'remote' ? <Wifi className="w-2.5 h-2.5" /> : <WifiOff className="w-2.5 h-2.5" />}
              {job.remote_type}
            </span>
          )}
          {job.employment_type && (
            <span className="badge-neutral">{job.employment_type}</span>
          )}
          {job.experience && (
            <span className="badge-brand text-xs">{job.experience}</span>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between mt-3">
          {job.salary ? (
            <span className="text-xs text-surface-400">
              {job.salary}
            </span>
          ) : <span />}

          <div className="flex items-center gap-2">
            <span className="text-xs text-surface-500">
              {job.discovered_at ? format(new Date(job.discovered_at), 'MMM d') : ''}
            </span>
            <Link
              to={`/jobs/${job.id}`}
              id={`btn-view-job-${job.id}`}
              className="btn-secondary btn-sm flex items-center gap-1"
            >
              View <ArrowRight className="w-3 h-3" />
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

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
    <div className="max-w-5xl space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="page-title">Job Search</h1>
          <p className="page-subtitle mt-1">
            {data ? `${data.total.toLocaleString()} jobs found` : 'Searching…'}
          </p>
        </div>
      </div>

      {/* Search Bar */}
      <form id="form-job-search" onSubmit={handleSearch} className="flex gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-surface-500" />
          <input
            id="input-job-keyword"
            type="text"
            placeholder="Job title, company, or skill…"
            value={localKeyword}
            onChange={(e) => setLocalKeyword(e.target.value)}
            className="input pl-10"
          />
        </div>
        <div className="relative">
          <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-surface-500" />
          <input
            id="input-job-location"
            type="text"
            placeholder="Location"
            value={filters.location ?? ''}
            onChange={(e) => setFilters({ location: e.target.value })}
            className="input pl-10 w-48"
          />
        </div>
        <button type="submit" id="btn-search" className="btn-primary px-5">
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
      </form>

      {/* Filters Panel */}
      {showFilters && (
        <div className="glass-card p-4 space-y-4 animate-slide-up">
          <div>
            <p className="text-xs font-semibold text-surface-400 uppercase tracking-wider mb-2">Work Mode</p>
            <div className="flex gap-2">
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
            <div key={i} className="glass-card p-5 space-y-3">
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
          <div className="glass-card p-12 empty-state">
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
        <div className="flex items-center justify-center gap-2">
          <button
            id="btn-prev-page"
            disabled={filters.page === 1}
            onClick={() => setFilters({ page: (filters.page ?? 1) - 1 })}
            className="btn-secondary btn-sm disabled:opacity-40"
          >
            Previous
          </button>
          <span className="text-sm text-surface-400">
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
