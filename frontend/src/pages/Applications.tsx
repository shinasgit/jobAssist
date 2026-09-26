import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import { ClipboardList, ExternalLink, Trash2, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import { applicationsApi } from '../services/applicationsApi';
import type { ApplicationStatus } from '../types';
import toast from 'react-hot-toast';
import { format } from 'date-fns';
import clsx from 'clsx';

const COLUMNS: { status: ApplicationStatus; label: string }[] = [
  { status: 'SAVED', label: 'Saved' },
  { status: 'PREPARING', label: 'Preparing' },
  { status: 'APPLIED', label: 'Applied' },
  { status: 'INTERVIEW', label: 'Interview' },
  { status: 'OFFER', label: 'Offer' },
  { status: 'REJECTED', label: 'Rejected' },
];

export default function Applications() {
  const qc = useQueryClient();
  const [activeStatus, setActiveStatus] = useState<ApplicationStatus | 'ALL'>('ALL');

  const { data: applications = [], isLoading } = useQuery({
    queryKey: ['applications'],
    queryFn: () => applicationsApi.list(),
  });

  const { mutate: deleteApp } = useMutation({
    mutationFn: applicationsApi.delete,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['applications'] });
      toast.success('Application removed');
    },
  });

  const filtered = activeStatus === 'ALL'
    ? applications
    : applications.filter((a) => a.status === activeStatus);

  return (
    <div className="max-w-5xl space-y-6">
      <div>
        <h1 className="page-title">Applications</h1>
        <p className="page-subtitle mt-1">{applications.length} total applications</p>
      </div>

      {/* Status Tabs */}
      <div className="flex gap-2 overflow-x-auto no-scrollbar pb-1">
        <button
          id="tab-all"
          onClick={() => setActiveStatus('ALL')}
          className={clsx('badge cursor-pointer whitespace-nowrap', activeStatus === 'ALL' ? 'badge-brand' : 'badge-neutral')}
        >
          All ({applications.length})
        </button>
        {COLUMNS.map(({ status, label }) => {
          const count = applications.filter((a) => a.status === status).length;
          return (
            <button
              key={status}
              id={`tab-${status.toLowerCase()}`}
              onClick={() => setActiveStatus(status)}
              className={clsx('badge cursor-pointer whitespace-nowrap', activeStatus === status ? 'badge-brand' : 'badge-neutral')}
            >
              {label} ({count})
            </button>
          );
        })}
      </div>

      {/* List */}
      {isLoading ? (
        <div className="space-y-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="skeleton h-20 rounded-xl" />
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <div className="glass-card p-12 empty-state">
          <ClipboardList className="w-12 h-12 text-surface-600 mb-4" />
          <p className="text-surface-300 font-medium">No applications yet</p>
          <p className="text-surface-500 text-sm mt-1">Save a job and prepare an application to get started</p>
          <Link to="/jobs" className="btn-primary btn-sm mt-4">Find Jobs</Link>
        </div>
      ) : (
        <div className="space-y-3">
          {filtered.map((app) => (
            <div key={app.id} id={`app-card-${app.id}`} className="glass-card p-4 flex items-center gap-4">
              <div className="w-10 h-10 rounded-xl bg-gradient-brand flex items-center justify-center text-xs font-bold text-white shrink-0">
                {app.job?.company ? app.job.company.charAt(0).toUpperCase() : '?'}
              </div>

              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold text-surface-100 truncate">{app.job?.title}</p>
                <p className="text-xs text-surface-400 truncate">{app.job?.company ?? 'Unknown Company'}</p>
              </div>

              <div className="flex items-center gap-3 shrink-0">
                <span className={clsx('badge', {
                  'badge-neutral': app.status === 'SAVED',
                  'badge-brand': app.status === 'PREPARING' || app.status === 'READY_TO_APPLY',
                  'badge-success': app.status === 'APPLIED' || app.status === 'OFFER',
                  'badge-warning': app.status === 'INTERVIEW',
                  'badge-danger': app.status === 'REJECTED',
                })}>
                  {app.status}
                </span>

                <span className="text-xs text-surface-500">
                  {format(new Date(app.updatedAt), 'MMM d')}
                </span>

                {app.job?.source_url && (
                  <a
                    href={app.job.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    id={`link-source-${app.id}`}
                    className="btn-ghost btn-sm p-1.5"
                  >
                    <ExternalLink className="w-3.5 h-3.5" />
                  </a>
                )}

                <Link
                  to={`/applications/${app.id}`}
                  id={`btn-view-app-${app.id}`}
                  className="btn-secondary btn-sm"
                >
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>

                <button
                  id={`btn-delete-app-${app.id}`}
                  onClick={() => deleteApp(app.id)}
                  className="btn-ghost btn-sm p-1.5 hover:text-danger hover:bg-danger/10"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
