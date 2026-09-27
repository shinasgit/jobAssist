import { useParams, Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { ArrowLeft, Bookmark, BookmarkCheck, ExternalLink } from 'lucide-react';
import { jobsApi } from '../services/jobsApi';
import toast from 'react-hot-toast';
import { format } from 'date-fns';
import clsx from 'clsx';
import DOMPurify from 'dompurify';

export default function JobDetails() {
  const { id } = useParams<{ id: string }>();
  const qc = useQueryClient();

  const { data: job, isLoading } = useQuery({
    queryKey: ['job', id],
    queryFn: () => jobsApi.get(id!),
    enabled: !!id,
  });

  const { mutate: toggleSave } = useMutation({
    mutationFn: async () => {
      if (job?.isSaved) await jobsApi.unsave(id!);
      else await jobsApi.save(id!);
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['job', id] });
      toast.success(job?.isSaved ? 'Removed from saved' : 'Job saved!');
    },
  });



  if (isLoading) {
    return (
      <div className="max-w-3xl space-y-4">
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
    <div className="max-w-3xl space-y-6 animate-fade-in">
      {/* Back */}
      <Link
        id="link-back-jobs"
        to="/jobs"
        className="inline-flex items-center gap-2 text-sm text-surface-400 hover:text-surface-100 transition-colors"
      >
        <ArrowLeft className="w-4 h-4" /> Back to Jobs
      </Link>

      {/* Header Card */}
      <div className="glass-card p-6">
        <div className="flex items-start gap-4">
          <div className="w-14 h-14 rounded-2xl bg-gradient-brand flex items-center justify-center text-lg font-bold text-white shrink-0">
            {job.company ? job.company.charAt(0).toUpperCase() : '?'}
          </div>

          <div className="flex-1 min-w-0">
            <h1 className="text-xl font-bold text-surface-50">{job.title}</h1>
            <p className="text-surface-400 text-sm mt-0.5">
              {job.company ?? 'Unknown Company'}
              {job.location && ` · ${job.location}`}
            </p>

            <div className="flex flex-wrap gap-2 mt-3">
              {job.remote_type && (
                <span className={clsx('badge', {
                  'badge-success': job.remote_type.toLowerCase() === 'remote',
                  'badge-brand': job.remote_type.toLowerCase() === 'hybrid',
                  'badge-neutral': job.remote_type.toLowerCase() === 'onsite',
                })}>
                  {job.remote_type}
                </span>
              )}
              {job.employment_type && (
                <span className="badge-neutral">{job.employment_type}</span>
              )}
              {job.posted_date && (
                <span className="badge-neutral">
                  Posted {format(new Date(job.posted_date), 'MMM d, yyyy')}
                </span>
              )}
              {job.experience && (
                <span className="badge-brand">{job.experience}</span>
              )}
            </div>
          </div>

          <div className="flex gap-2 shrink-0">
            <button
              id="btn-save-job"
              onClick={() => toggleSave()}
              className="btn-secondary"
            >
              {job.isSaved ? (
                <>
                  <BookmarkCheck className="w-4 h-4 text-yellow-400" />
                  Saved
                </>
              ) : (
                <>
                  <Bookmark className="w-4 h-4" />
                  Save Job
                </>
              )}
            </button>
            <a
              id="link-source"
              href={job.source_url ?? '#'}
              target="_blank"
              rel="noopener noreferrer"
              className="btn-secondary"
            >
              <ExternalLink className="w-4 h-4" />
            </a>
          </div>
        </div>

        {/* Salary */}
        {job.salary && (
          <div className="mt-4 p-3 bg-success/5 border border-success/20 rounded-xl">
            <p className="text-sm text-success font-medium">
              {job.salary}
            </p>
          </div>
        )}


      </div>

      {/* Description */}
      <div className="glass-card p-6">
        <h2 className="text-sm font-semibold text-surface-300 uppercase tracking-wider mb-4">Job Description</h2>
        <div 
          className="text-sm text-surface-300 leading-relaxed prose prose-invert max-w-none"
          dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(job.description || '') }}
        />
      </div>

    </div>
  );
}
