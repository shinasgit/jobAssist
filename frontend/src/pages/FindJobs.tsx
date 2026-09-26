import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { jobsApi } from '../services/jobsApi';
import toast from 'react-hot-toast';
import { Search, Loader2 } from 'lucide-react';

import { useNavigate } from 'react-router-dom';

export default function FindJobs() {
  const [keyword, setKeyword] = useState('');
  const [location, setLocation] = useState('');
  const [experience, setExperience] = useState('Fresher');
  const [remoteType, setRemoteType] = useState('any');
  const navigate = useNavigate();

  const { mutate: handleSearch, isPending } = useMutation({
    mutationFn: () => {
      console.log('1. Form Submitted! Sending these parameters to backend API:', { keyword, location, experience, remoteType });
      return jobsApi.search({ keyword, location, experience, remote_type: remoteType });
    },
    onSuccess: (data) => {
      console.log('2. Success! The backend FastAPI server replied with:', data);
      toast.success('Search request sent to backend!');
      // Navigate to the jobs list to view the results
      navigate('/jobs');
    },
    onError: (err: any) => {
      console.error('Error occurred:', err);
      toast.error(err?.response?.data?.detail ?? err?.message ?? 'Failed to search');
    }
  });

  const onSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!keyword.trim()) {
      toast.error('Keyword is required');
      return;
    }
    console.log('0. Button clicked. Preparing to send request...');
    handleSearch();
  };

  return (
    <div className="max-w-3xl mx-auto space-y-8">
      <div>
        <h1 className="page-title">Find Jobs</h1>
        <p className="page-subtitle mt-1">Search via Backend API</p>
      </div>

      <div className="glass-card p-6">
        <form onSubmit={onSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-surface-300 mb-1">Keyword</label>
            <input 
              type="text" 
              placeholder="e.g. Junior AI Developer" 
              value={keyword}
              onChange={e => setKeyword(e.target.value)}
              className="input w-full"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-surface-300 mb-1">Location</label>
            <input 
              type="text" 
              placeholder="e.g. Bangalore" 
              value={location}
              onChange={e => setLocation(e.target.value)}
              className="input w-full"
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-surface-300 mb-1">Experience</label>
              <select value={experience} onChange={e => setExperience(e.target.value)} className="input w-full">
                <option value="Fresher">Fresher (0-2 years)</option>
                <option value="Mid">Mid Level (2-5 years)</option>
                <option value="Senior">Senior (5+ years)</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-surface-300 mb-1">Remote Type</label>
              <select value={remoteType} onChange={e => setRemoteType(e.target.value)} className="input w-full">
                <option value="any">Any</option>
                <option value="remote">Remote</option>
                <option value="hybrid">Hybrid</option>
                <option value="onsite">On-site</option>
              </select>
            </div>
          </div>
          <button type="submit" disabled={isPending} className="btn-primary w-full justify-center">
            {isPending ? <Loader2 className="w-5 h-5 animate-spin" /> : <Search className="w-5 h-5" />}
            {isPending ? 'Sending...' : 'Find Jobs'}
          </button>
        </form>
      </div>
    </div>
  );
}
