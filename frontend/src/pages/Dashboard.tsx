import { useQuery } from '@tanstack/react-query';
import {
  Briefcase, Sparkles, ArrowRight, AlertTriangle, RefreshCw, Clock, Globe, Sliders
} from 'lucide-react';
import { dashboardApi } from '../services/dashboardApi';
import { Link } from 'react-router-dom';
import { format } from 'date-fns';
import clsx from 'clsx';

function StatCard({
  label,
  value,
  subtext,
  icon: Icon,
  color,
  bg,
  to,
}: {
  label: string;
  value: string | number;
  subtext?: string;
  icon: React.ElementType;
  color: string;
  bg: string;
  to: string;
}) {
  return (
    <Link
      to={to}
      className="glass-card-hover p-4 sm:p-5 flex flex-col justify-between min-w-0 group cursor-pointer transition-all duration-200"
    >
      <div className="flex items-center justify-between gap-2">
        <span className="text-xs sm:text-sm text-surface-400 font-medium truncate">{label}</span>
        <div className={clsx('p-2 rounded-xl shrink-0 transition-transform group-hover:scale-110', bg)}>
          <Icon className={clsx('w-4 h-4 sm:w-5 sm:h-5', color)} />
        </div>
      </div>
      <div className="flex items-baseline justify-between mt-3">
        <div>
          <span className="text-2xl sm:text-3xl font-bold tracking-tight text-surface-50">{value}</span>
          {subtext && <p className="text-[11px] text-surface-400 mt-0.5">{subtext}</p>}
        </div>
        <ArrowRight className="w-4 h-4 text-surface-600 group-hover:text-surface-300 group-hover:translate-x-1 transition-all" />
      </div>
    </Link>
  );
}

function SkeletonStatCard() {
  return (
    <div className="glass-card p-4 sm:p-5 space-y-3">
      <div className="flex justify-between items-center">
        <div className="skeleton h-3 w-20" />
        <div className="skeleton h-8 w-8 rounded-xl" />
      </div>
      <div className="skeleton h-7 w-16 mt-2" />
    </div>
  );
}

export default function Dashboard() {
  const { data, isLoading, isError, error, refetch, isFetching } = useQuery({
    queryKey: ['dashboard-summary'],
    queryFn: () => dashboardApi.getSummary(),
  });

  const hour = new Date().getHours();
  const greeting = hour < 12 ? 'Good morning' : hour < 18 ? 'Good afternoon' : 'Good evening';

  const STATS_CONFIG = [
    { label: 'Total Jobs', value: data?.total_jobs?.toLocaleString() ?? '0', subtext: 'In SQLite database', icon: Briefcase, color: 'text-brand-400', bg: 'bg-brand-500/10', to: '/jobs' },
    { label: 'New Jobs (7d)', value: data?.new_jobs?.toLocaleString() ?? '0', subtext: 'Discovered recently', icon: Clock, color: 'text-emerald-400', bg: 'bg-emerald-500/10', to: '/jobs' },
    { label: 'Active Sources', value: '3 Active', subtext: 'Himalayas, Remotive, Arbeitnow', icon: Globe, color: 'text-blue-400', bg: 'bg-blue-500/10', to: '/settings' },
    { label: 'Search Preferences', value: 'Configured', subtext: 'Default filters saved', icon: Sliders, color: 'text-purple-400', bg: 'bg-purple-500/10', to: '/settings' },
  ];

  return (
    <div className="space-y-6 sm:space-y-8 max-w-7xl mx-auto w-full min-w-0">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl sm:text-2xl lg:text-3xl font-bold tracking-tight text-surface-50">
            {greeting},{' '}
            <span className="text-gradient">Welcome back</span> 👋
          </h1>
          <p className="text-xs sm:text-sm text-surface-400 mt-1">Multi-source job aggregator & real-time search engine</p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => refetch()}
            disabled={isFetching}
            className="btn-secondary btn-sm flex items-center gap-1.5"
            title="Refresh Dashboard Data"
          >
            <RefreshCw className={clsx('w-3.5 h-3.5', isFetching && 'animate-spin')} />
            <span className="hidden sm:inline">Refresh</span>
          </button>

          <Link
            id="btn-find-jobs"
            to="/find-jobs"
            className="btn-primary flex-1 sm:flex-initial justify-center"
          >
            <Sparkles className="w-4 h-4" />
            Find Jobs
          </Link>
        </div>
      </div>

      {/* Error State */}
      {isError ? (
        <div className="glass-card p-6 sm:p-8 text-center flex flex-col items-center justify-center border-danger/20 bg-danger/5">
          <AlertTriangle className="w-10 h-10 text-danger mb-3" />
          <p className="text-surface-200 font-semibold text-base">Unable to load dashboard data.</p>
          <p className="text-surface-400 text-xs sm:text-sm mt-1 mb-4">
            {error instanceof Error ? error.message : 'Backend request failed'}
          </p>
          <button onClick={() => refetch()} className="btn-primary btn-sm flex items-center gap-2">
            <RefreshCw className="w-4 h-4" /> Retry
          </button>
        </div>
      ) : (
        <>
          {/* Stats Grid */}
          <div>
            <h2 className="text-xs sm:text-sm font-semibold text-surface-400 uppercase tracking-wider mb-3">Database Overview</h2>
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
              {isLoading
                ? Array.from({ length: 4 }).map((_, i) => <SkeletonStatCard key={i} />)
                : STATS_CONFIG.map((stat) => (
                    <StatCard key={stat.label} {...stat} />
                  ))}
            </div>
          </div>

          {/* Recent Jobs Discovered */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h2 className="text-xs sm:text-sm font-semibold text-surface-400 uppercase tracking-wider">
                Recent Jobs Discovered
              </h2>
              <Link to="/jobs" className="text-xs text-brand-400 hover:text-brand-300 flex items-center gap-1 font-medium">
                View all jobs <ArrowRight className="w-3 h-3" />
              </Link>
            </div>

            {isLoading ? (
              <div className="space-y-3">
                {Array.from({ length: 4 }).map((_, i) => (
                  <div key={i} className="glass-card p-4 space-y-2">
                    <div className="skeleton h-4 w-48" />
                    <div className="skeleton h-3 w-32" />
                  </div>
                ))}
              </div>
            ) : !data?.recent_jobs?.length ? (
              <div className="glass-card p-8 sm:p-12 text-center flex flex-col items-center justify-center">
                <Briefcase className="w-12 h-12 text-surface-600 mb-3" />
                <p className="text-surface-300 text-base font-medium">No jobs discovered yet</p>
                <p className="text-surface-500 text-xs sm:text-sm mt-1 mb-6">Run a multi-source search to fetch jobs into SQLite</p>
                <Link to="/find-jobs" className="btn-primary">
                  <Sparkles className="w-4 h-4 mr-2" />
                  Find Jobs Now
                </Link>
              </div>
            ) : (
              <div className="space-y-2.5">
                {data.recent_jobs.map((job) => (
                  <Link
                    key={job.id}
                    to={`/jobs/${job.id}`}
                    className="glass-card-hover p-4 flex items-center gap-3.5 min-w-0"
                  >
                    <div className="w-10 h-10 rounded-xl bg-gradient-brand flex items-center justify-center text-xs font-bold text-white shrink-0">
                      {job.company ? job.company.charAt(0).toUpperCase() : '?'}
                    </div>

                    <div className="flex-1 min-w-0">
                      <p className="text-xs sm:text-sm font-semibold text-surface-100 truncate">{job.title}</p>
                      <p className="text-[11px] sm:text-xs text-surface-400 truncate">
                        {job.company ?? 'Unknown'} {job.location && `· ${job.location}`}
                      </p>
                    </div>

                    <div className="flex items-center gap-3 shrink-0">
                      {job.source && (
                        <span className="badge-neutral text-[10px] sm:text-xs capitalize font-medium hidden sm:inline-flex">
                          {job.source}
                        </span>
                      )}
                      {job.remote_type && (
                        <span className={clsx('badge text-[10px] px-2 py-0.5', {
                          'badge-success': job.remote_type.toLowerCase() === 'remote',
                          'badge-brand': job.remote_type.toLowerCase() === 'hybrid',
                          'badge-neutral': job.remote_type.toLowerCase() === 'onsite',
                        })}>
                          {job.remote_type}
                        </span>
                      )}
                      <span className="text-[10px] sm:text-xs text-surface-500">
                        {job.discovered_at ? format(new Date(job.discovered_at), 'MMM d') : ''}
                      </span>
                      <ArrowRight className="w-4 h-4 text-surface-600 hidden sm:block" />
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
