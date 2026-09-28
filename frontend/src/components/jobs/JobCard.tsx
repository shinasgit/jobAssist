import { Wifi, WifiOff, ArrowRight, Globe, ExternalLink } from 'lucide-react';
import { Link } from 'react-router-dom';
import type { Job } from '../../types';
import { format } from 'date-fns';
import clsx from 'clsx';

export function JobCard({ job }: { job: Job & { isSaved?: boolean; isApplied?: boolean } }) {
  return (
    <div className="glass-card p-4 sm:p-5 flex flex-col sm:flex-row gap-3 sm:gap-4 group animate-slide-up w-full min-w-0">
      {/* Top Header Row on Mobile */}
      <div className="flex items-start gap-3 sm:gap-4 flex-1 min-w-0">
        {/* Logo */}
        <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-xl bg-gradient-brand flex items-center justify-center text-xs sm:text-sm font-bold text-white shrink-0">
          {job.company ? job.company.charAt(0).toUpperCase() : '?'}
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <div className="min-w-0">
              <Link
                id={`job-title-${job.id}`}
                to={`/jobs/${job.id}`}
                className="text-sm font-semibold text-surface-100 hover:text-brand-300 transition-colors line-clamp-2 break-words"
              >
                {job.title}
              </Link>
              <p className="text-xs text-surface-400 mt-0.5 truncate">
                {job.company ?? 'Unknown Company'}
                {job.location && ` · ${job.location}`}
              </p>
            </div>
          </div>

          {/* Badges & Tags */}
          <div className="flex flex-wrap items-center gap-1.5 mt-2">
            {job.source && (
              <span className="badge-neutral text-[10px] sm:text-xs flex items-center gap-1 capitalize font-medium">
                <Globe className="w-2.5 h-2.5 text-surface-400" /> {job.source}
              </span>
            )}
            {job.remote_type && (
              <span className={clsx('badge text-[10px] sm:text-xs', {
                'badge-success': job.remote_type.toLowerCase() === 'remote',
                'badge-brand': job.remote_type.toLowerCase() === 'hybrid',
                'badge-neutral': job.remote_type.toLowerCase() === 'onsite',
              })}>
                {job.remote_type.toLowerCase() === 'remote' ? <Wifi className="w-2.5 h-2.5" /> : <WifiOff className="w-2.5 h-2.5" />}
                {job.remote_type}
              </span>
            )}
            {job.employment_type && (
              <span className="badge-neutral text-[10px] sm:text-xs">{job.employment_type}</span>
            )}
            {job.experience && (
              <span className="badge-brand text-[10px] sm:text-xs">{job.experience}</span>
            )}
          </div>
        </div>
      </div>

      {/* Footer / Actions Row */}
      <div className="flex items-center justify-between sm:justify-end gap-2 border-t sm:border-t-0 border-surface-800/60 pt-2.5 sm:pt-0 mt-1 sm:mt-0">
        <div className="flex items-center gap-2">
          {job.salary ? (
            <span className="text-xs text-emerald-400 font-medium truncate max-w-[120px] sm:max-w-none">
              {job.salary}
            </span>
          ) : (
            <span className="text-[11px] text-surface-500">
              {job.discovered_at ? format(new Date(job.discovered_at), 'MMM d') : ''}
            </span>
          )}
        </div>

        <div className="flex items-center gap-2 shrink-0">
          {job.source_url && (
            <a
              href={job.source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="btn-ghost btn-sm text-xs py-1.5 px-2.5 min-h-[36px] flex items-center gap-1 text-surface-400 hover:text-surface-100"
              title="Open Original Listing"
            >
              <ExternalLink className="w-3.5 h-3.5" />
            </a>
          )}

          <Link
            to={`/jobs/${job.id}`}
            id={`btn-view-job-${job.id}`}
            className="btn-primary btn-sm flex items-center gap-1 py-1.5 px-3 min-h-[36px] text-xs"
          >
            <span>View Details</span> <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      </div>
    </div>
  );
}
