import { useQuery } from '@tanstack/react-query';
import {
  Briefcase, Bookmark, ClipboardList, TrendingUp,
  Award, XCircle, ArrowRight, Sparkles,
} from 'lucide-react';
import { jobsApi } from '../services/jobsApi';
import { api } from '../services/api';

import { Link } from 'react-router-dom';
import { format } from 'date-fns';
import clsx from 'clsx';

const STAT_CONFIG = [
  { key: 'jobsDiscovered', label: 'Jobs Discovered', icon: Briefcase, color: 'text-brand-400', bg: 'bg-brand-500/10' },
  { key: 'savedJobs', label: 'Saved Jobs', icon: Bookmark, color: 'text-yellow-400', bg: 'bg-yellow-500/10' },
  { key: 'applications', label: 'Applications', icon: ClipboardList, color: 'text-blue-400', bg: 'bg-blue-500/10' },
  { key: 'interviews', label: 'Interviews', icon: TrendingUp, color: 'text-green-400', bg: 'bg-green-500/10' },
  { key: 'offers', label: 'Offers', icon: Award, color: 'text-purple-400', bg: 'bg-purple-500/10' },
  { key: 'rejections', label: 'Rejections', icon: XCircle, color: 'text-surface-500', bg: 'bg-surface-800' },
];

function StatCard({
  label,
  value,
  icon: Icon,
  color,
  bg,
}: {
  label: string;
  value: number;
  icon: React.ElementType;
  color: string;
  bg: string;
}) {
  return (
    <div className="stat-card animate-slide-up">
      <div className="flex items-center justify-between">
        <span className="text-sm text-surface-400">{label}</span>
        <div className={clsx('p-2 rounded-xl', bg)}>
          <Icon className={clsx('w-4 h-4', color)} />
        </div>
      </div>
      <span className="text-3xl font-bold text-surface-50">{value}</span>
    </div>
  );
}

function SkeletonCard() {
  return (
    <div className="glass-card p-5 space-y-3">
      <div className="skeleton h-4 w-24" />
      <div className="skeleton h-8 w-16" />
    </div>
  );
}

export default function Dashboard() {
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: async () => {
      // Mock stats for Phase 1
      return {
        jobsDiscovered: 42,
        savedJobs: 8,
        applications: 5,
        interviews: 1,
        offers: 0,
        rejections: 2
      };
    },
  });

  const { data: recentJobs, isLoading: jobsLoading } = useQuery({
    queryKey: ['recent-jobs'],
    queryFn: () => jobsApi.list({ limit: 5, page: 1 }),
  });

  const hour = new Date().getHours();
  const greeting = hour < 12 ? 'Good morning' : hour < 18 ? 'Good afternoon' : 'Good evening';

  return (
    <div className="space-y-8 max-w-6xl">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="page-title">
            {greeting},{' '}
            <span className="text-gradient">Welcome back</span> 👋
          </h1>
          <p className="page-subtitle mt-1">Here's what's happening with your job search</p>
        </div>
        <Link
          id="btn-find-jobs"
          to="/jobs"
          className="btn-primary"
        >
          <Sparkles className="w-4 h-4" />
          Find Jobs
        </Link>
      </div>

      {/* Stats Grid */}
      <div>
        <h2 className="text-sm font-semibold text-surface-400 uppercase tracking-wider mb-3">Overview</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
          {statsLoading
            ? Array.from({ length: 6 }).map((_, i) => <SkeletonCard key={i} />)
            : STAT_CONFIG.map(({ key, label, icon, color, bg }) => (
                <StatCard
                  key={key}
                  label={label}
                  value={stats?.[key as keyof typeof stats] ?? 0}
                  icon={icon}
                  color={color}
                  bg={bg}
                />
              ))}
        </div>
      </div>

      {/* Recent Jobs */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-sm font-semibold text-surface-400 uppercase tracking-wider">
            Recent Jobs
          </h2>
          <Link id="link-all-jobs" to="/jobs" className="text-xs text-brand-400 hover:text-brand-300 flex items-center gap-1 transition-colors">
            View all <ArrowRight className="w-3 h-3" />
          </Link>
        </div>

        {jobsLoading ? (
          <div className="space-y-3">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="glass-card p-4">
                <div className="skeleton h-4 w-48 mb-2" />
                <div className="skeleton h-3 w-32" />
              </div>
            ))}
          </div>
        ) : recentJobs?.items?.length === 0 ? (
          <div className="glass-card p-8 empty-state">
            <Briefcase className="w-10 h-10 text-surface-600 mb-3" />
            <p className="text-surface-400 text-sm">No jobs discovered yet.</p>
            <Link to="/jobs" className="btn-primary btn-sm mt-4">
              Search Jobs
            </Link>
          </div>
        ) : (
          <div className="space-y-3">
            {recentJobs?.items?.map((job) => (
              <Link
                key={job.id}
                id={`job-card-${job.id}`}
                to={`/jobs/${job.id}`}
                className="glass-card-hover p-4 flex items-center gap-4"
              >
                {/* Company avatar */}
                <div className="w-10 h-10 rounded-xl bg-gradient-brand flex items-center justify-center text-xs font-bold text-white shrink-0">
                  {job.company ? job.company.charAt(0).toUpperCase() : '?'}
                </div>

                <div className="flex-1 min-w-0">
                  <p className="text-sm font-semibold text-surface-100 truncate">{job.title}</p>
                  <p className="text-xs text-surface-400 truncate">
                    {job.company ?? 'Unknown Company'}
                    {job.location && ` · ${job.location}`}
                  </p>
                </div>

                <div className="flex flex-col items-end gap-1.5 shrink-0">
                  {job.remote_type && (
                    <span className={clsx('badge', {
                      'badge-success': job.remote_type.toLowerCase() === 'remote',
                      'badge-brand': job.remote_type.toLowerCase() === 'hybrid',
                      'badge-neutral': job.remote_type.toLowerCase() === 'onsite',
                    })}>
                      {job.remote_type}
                    </span>
                  )}
                  <span className="text-xs text-surface-500">
                    {job.discovered_at ? format(new Date(job.discovered_at), 'MMM d') : ''}
                  </span>
                </div>

                <ArrowRight className="w-4 h-4 text-surface-600 shrink-0" />
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
