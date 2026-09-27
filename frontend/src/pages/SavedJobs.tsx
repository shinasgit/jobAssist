import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { Bookmark, Search } from 'lucide-react';
import { jobsApi } from '../services/jobsApi';
import { JobCard } from '../components/jobs/JobCard';

export default function SavedJobs() {
  const { data, isLoading } = useQuery({
    queryKey: ['savedJobs'],
    queryFn: () => jobsApi.getSaved(),
  });

  return (
    <div className="max-w-4xl space-y-8 animate-fade-in">
      <div>
        <h1 className="page-title">Saved Jobs</h1>
        <p className="page-subtitle mt-1">
          {data?.items ? `${data.items.length} saved jobs` : 'Jobs you have manually saved for later'}
        </p>
      </div>

      <div className="space-y-4">
        {isLoading ? (
          Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="glass-card p-5 space-y-3">
              <div className="flex gap-4">
                <div className="skeleton w-12 h-12 rounded-xl" />
                <div className="flex-1 space-y-2">
                  <div className="skeleton h-4 w-48" />
                  <div className="skeleton h-3 w-32" />
                </div>
              </div>
            </div>
          ))
        ) : !data?.items?.length ? (
          <div className="glass-card p-12 empty-state">
            <Bookmark className="w-12 h-12 text-surface-600 mb-4" />
            <p className="text-surface-300 font-medium">No saved jobs yet.</p>
            <p className="text-surface-500 text-sm mt-1 mb-6">Find a job you are interested in and click "Save Job" to keep it here.</p>
            <Link to="/jobs" className="btn-primary">
              <Search className="w-4 h-4 mr-2" />
              Find Jobs
            </Link>
          </div>
        ) : (
          data.items.map((job) => (
            <JobCard key={job.id} job={job} />
          ))
        )}
      </div>
    </div>
  );
}
