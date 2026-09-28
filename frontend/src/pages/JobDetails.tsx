import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { ArrowLeft, ExternalLink, Globe } from 'lucide-react';
import { jobsApi } from '../services/jobsApi';
import { format } from 'date-fns';
import clsx from 'clsx';
import DOMPurify from 'dompurify';

export default function JobDetails() {
  const { id } = useParams<{ id: string }>();

  const { data: job, isLoading } = useQuery({
    queryKey: ['job', id],
    queryFn: () => jobsApi.get(id!),
    enabled: !!id,
  });

  if (isLoading) {
    return (
      <div className="max-w-3xl mx-auto space-y-4 w-full">
        <div className="skeleton h-8 w-48" />
        <div className="glass-card p-6 space-y-4">
          <div className="skeleton h-6 w-64" />
          <div className="skeleton h-4 w-40" />
          <div className="skeleton h-32 w-full" />
        </div>
      </div>
    );
  }

  if (!job) {
    return (
      <div className="empty-state">
        <p className="text-surface-400">Job not found</p>
        <Link to="/jobs" className="btn-secondary btn-sm mt-4">Back to Jobs</Link>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6 animate-fade-in w-full min-w-0">
      {/* Back */}
      <Link
        id="link-back-jobs"
        to="/jobs"
        className="inline-flex items-center gap-2 text-xs sm:text-sm text-surface-400 hover:text-surface-100 transition-colors"
      >
        <ArrowLeft className="w-4 h-4" /> Back to Jobs
      </Link>

      {/* Header Card */}
      <div className="glass-card p-4 sm:p-6 w-full">
        <div className="flex flex-col sm:flex-row items-start gap-4">
          <div className="w-12 h-12 sm:w-14 sm:h-14 rounded-2xl bg-gradient-brand flex items-center justify-center text-base sm:text-lg font-bold text-white shrink-0">
            {job.company ? job.company.charAt(0).toUpperCase() : '?'}
          </div>

          <div className="flex-1 min-w-0 w-full">
            <h1 className="text-lg sm:text-xl font-bold text-surface-50 break-words">{job.title}</h1>
            <p className="text-surface-400 text-xs sm:text-sm mt-0.5">
              {job.company ?? 'Unknown Company'}
              {job.location && ` · ${job.location}`}
            </p>

            <div className="flex flex-wrap gap-2 mt-3">
              {job.source && (
                <span className="badge-neutral text-xs capitalize flex items-center gap-1 font-medium">
                  <Globe className="w-3 h-3 text-surface-400" /> {job.source}
                </span>
              )}
              {job.remote_type && (
                <span className={clsx('badge text-xs', {
                  'badge-success': job.remote_type.toLowerCase() === 'remote',
                  'badge-brand': job.remote_type.toLowerCase() === 'hybrid',
                  'badge-neutral': job.remote_type.toLowerCase() === 'onsite',
                })}>
                  {job.remote_type}
                </span>
              )}
              {job.employment_type && (
                <span className="badge-neutral text-xs">{job.employment_type}</span>
              )}
              {job.posted_date && (
                <span className="badge-neutral text-xs">
                  Posted {format(new Date(job.posted_date), 'MMM d, yyyy')}
                </span>
              )}
              {job.experience && (
                <span className="badge-brand text-xs">{job.experience}</span>
              )}
            </div>
          </div>
        </div>

        {/* Action Buttons Row */}
        {job.source_url && (
          <div className="flex flex-wrap items-center gap-2 mt-4 pt-4 border-t border-surface-800/80">
            <a
              id="link-source"
              href={job.source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="btn-primary w-full sm:w-auto justify-center gap-2 min-h-[44px]"
            >
              <span>Open Original Job Listing</span> <ExternalLink className="w-4 h-4" />
            </a>
          </div>
        )}

        {/* Salary */}
        {job.salary && (
          <div className="mt-4 p-3 bg-success/5 border border-success/20 rounded-xl">
            <p className="text-xs sm:text-sm text-success font-medium">
              {job.salary}
            </p>
          </div>
        )}
      </div>

      {/* Description */}
      <div className="glass-card p-4 sm:p-6 w-full">
        <h2 className="text-xs sm:text-sm font-semibold text-surface-300 uppercase tracking-wider mb-4">Job Description</h2>
        <div 
          className="text-xs sm:text-sm text-surface-300 leading-relaxed prose prose-invert max-w-none overflow-x-auto break-words"
          dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(job.description || '') }}
        />
      </div>
    </div>
  );
}
