import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Bookmark, BookmarkCheck, Wifi, WifiOff, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import { jobsApi } from '../../services/jobsApi';
import type { Job } from '../../types';
import { format } from 'date-fns';
import toast from 'react-hot-toast';
import clsx from 'clsx';

export function JobCard({ job }: { job: Job & { isSaved?: boolean } }) {
  const qc = useQueryClient();

  const { mutate: toggleSave, isPending } = useMutation({
    mutationFn: async () => {
      if (job.isSaved) await jobsApi.unsave(job.id);
      else await jobsApi.save(job.id);
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['jobs'] });
      qc.invalidateQueries({ queryKey: ['savedJobs'] });
      qc.invalidateQueries({ queryKey: ['job', job.id.toString()] });
      toast.success(job.isSaved ? 'Job removed from saved' : 'Job saved!');
    },
    onError: () => {
      toast.error('Failed to update saved status');
    }
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
