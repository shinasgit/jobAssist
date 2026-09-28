import { useState, useEffect } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { jobsApi } from '../services/jobsApi';
import { settingsApi } from '../services/settingsApi';
import toast from 'react-hot-toast';
import { Search, Loader2 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function FindJobs() {
  const [keyword, setKeyword] = useState('');
  const [location, setLocation] = useState('');
  const [experience, setExperience] = useState('Fresher');
  const [remoteType, setRemoteType] = useState('any');
  const navigate = useNavigate();

  // Load saved default settings
  const { data: settings } = useQuery({
    queryKey: ['settings'],
    queryFn: () => settingsApi.get(),
  });

  useEffect(() => {
    if (settings) {
      if (settings.keywords && settings.keywords.length > 0) {
        setKeyword(settings.keywords[0]);
      }
      if (settings.locations && settings.locations.length > 0) {
        setLocation(settings.locations[0]);
      }
      if (settings.experience) {
        setExperience(settings.experience);
      }
      if (settings.remote_type) {
        setRemoteType(settings.remote_type);
      }
    }
  }, [settings]);

  const { mutate: handleSearch, isPending } = useMutation({
    mutationFn: () => {
      return jobsApi.search({ keyword, location, experience, remote_type: remoteType });
    },
    onSuccess: () => {
      toast.success('Search request sent to backend!');
      navigate('/jobs');
    },
    onError: (err: any) => {
      toast.error(err?.response?.data?.detail ?? err?.message ?? 'Failed to search');
    }
  });

  const onSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!keyword.trim()) {
      toast.error('Keyword is required');
      return;
    }
    handleSearch();
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6 sm:space-y-8 w-full min-w-0">
      <div>
        <h1 className="text-xl sm:text-2xl lg:text-3xl font-bold tracking-tight text-surface-50">Find Jobs</h1>
        <p className="text-xs sm:text-sm text-surface-400 mt-1">Search via Multi-Source Backend Aggregator</p>
      </div>

      <div className="glass-card p-4 sm:p-6 w-full">
        <form onSubmit={onSubmit} className="space-y-4">
          <div>
            <label className="block text-xs sm:text-sm font-medium text-surface-300 mb-1">Keyword</label>
            <input 
              type="text" 
              placeholder="e.g. Junior AI Developer" 
              value={keyword}
              onChange={e => setKeyword(e.target.value)}
              className="input w-full text-xs sm:text-sm"
            />
          </div>
          <div>
            <label className="block text-xs sm:text-sm font-medium text-surface-300 mb-1">Location</label>
            <input 
              type="text" 
              placeholder="e.g. Bangalore" 
              value={location}
              onChange={e => setLocation(e.target.value)}
              className="input w-full text-xs sm:text-sm"
            />
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs sm:text-sm font-medium text-surface-300 mb-1">Experience</label>
              <select value={experience} onChange={e => setExperience(e.target.value)} className="input w-full text-xs sm:text-sm">
                <option value="Fresher">Fresher (0-2 years)</option>
                <option value="Mid">Mid Level (2-5 years)</option>
                <option value="Senior">Senior (5+ years)</option>
              </select>
            </div>
            <div>
              <label className="block text-xs sm:text-sm font-medium text-surface-300 mb-1">Remote Type</label>
              <select value={remoteType} onChange={e => setRemoteType(e.target.value)} className="input w-full text-xs sm:text-sm">
                <option value="any">Any</option>
                <option value="remote">Remote</option>
                <option value="hybrid">Hybrid</option>
                <option value="onsite">On-site</option>
              </select>
            </div>
          </div>
          <button type="submit" disabled={isPending} className="btn-primary w-full justify-center min-h-[44px]">
            {isPending ? <Loader2 className="w-5 h-5 animate-spin" /> : <Search className="w-5 h-5" />}
            {isPending ? 'Searching Multi-Source...' : 'Find Jobs'}
          </button>
        </form>
      </div>
    </div>
  );
}
