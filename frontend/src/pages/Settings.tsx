import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { settingsApi } from '../services/settingsApi';
import type { UserSettings } from '../types';
import toast from 'react-hot-toast';
import { Sliders, Plus, X, Globe, Save, Loader2 } from 'lucide-react';

const AVAILABLE_SOURCES = [
  { id: 'himalayas', label: 'Himalayas' },
  { id: 'remotive', label: 'Remotive' },
  { id: 'arbeitnow', label: 'Arbeitnow' },
];

const EMPLOYMENT_OPTIONS = ['Full-time', 'Part-time', 'Internship', 'Contract'];

export default function Settings() {
  const qc = useQueryClient();

  const [keywords, setKeywords] = useState<string[]>([]);
  const [newKeyword, setNewKeyword] = useState('');
  
  const [locations, setLocations] = useState<string[]>([]);
  const [newLocation, setNewLocation] = useState('');
  
  const [experience, setExperience] = useState('Fresher');
  const [remoteType, setRemoteType] = useState('any');
  const [employmentTypes, setEmploymentTypes] = useState<string[]>(['Full-time']);
  const [enabledSources, setEnabledSources] = useState<string[]>(['himalayas', 'remotive', 'arbeitnow']);

  const { data: settingsData, isLoading } = useQuery({
    queryKey: ['settings'],
    queryFn: () => settingsApi.get(),
  });

  useEffect(() => {
    if (settingsData) {
      setKeywords(settingsData.keywords ?? []);
      setLocations(settingsData.locations ?? []);
      setExperience(settingsData.experience ?? 'Fresher');
      setRemoteType(settingsData.remote_type ?? 'any');
      setEmploymentTypes(settingsData.employment_types ?? ['Full-time']);
      setEnabledSources(settingsData.enabled_sources ?? ['himalayas', 'remotive', 'arbeitnow']);
    }
  }, [settingsData]);

  const { mutate: saveSettings, isPending } = useMutation({
    mutationFn: (data: Partial<UserSettings>) => settingsApi.update(data),
    onSuccess: (updated) => {
      qc.invalidateQueries({ queryKey: ['settings'] });
      toast.success('Search preferences saved!');
    },
    onError: (err: any) => {
      toast.error(err?.response?.data?.detail ?? err?.message ?? 'Failed to save settings');
    }
  });

  const handleAddKeyword = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    const val = newKeyword.trim();
    if (!val) return;
    if (keywords.some(k => k.toLowerCase() === val.toLowerCase())) {
      toast.error('Keyword already added');
      return;
    }
    setKeywords([...keywords, val]);
    setNewKeyword('');
  };

  const handleRemoveKeyword = (index: number) => {
    setKeywords(keywords.filter((_, i) => i !== index));
  };

  const handleAddLocation = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    const val = newLocation.trim();
    if (!val) return;
    if (locations.some(l => l.toLowerCase() === val.toLowerCase())) {
      toast.error('Location already added');
      return;
    }
    setLocations([...locations, val]);
    setNewLocation('');
  };

  const handleRemoveLocation = (index: number) => {
    setLocations(locations.filter((_, i) => i !== index));
  };

  const toggleEmployment = (emp: string) => {
    if (employmentTypes.includes(emp)) {
      setEmploymentTypes(employmentTypes.filter(e => e !== emp));
    } else {
      setEmploymentTypes([...employmentTypes, emp]);
    }
  };

  const toggleSource = (srcId: string) => {
    if (enabledSources.includes(srcId)) {
      if (enabledSources.length === 1) {
        toast.error('At least one source must remain enabled');
        return;
      }
      setEnabledSources(enabledSources.filter(s => s !== srcId));
    } else {
      setEnabledSources([...enabledSources, srcId]);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    saveSettings({
      keywords,
      locations,
      experience,
      remote_type: remoteType,
      employment_types: employmentTypes,
      enabled_sources: enabledSources,
    });
  };

  if (isLoading) {
    return (
      <div className="max-w-3xl mx-auto space-y-4 w-full">
        <div className="skeleton h-8 w-48" />
        <div className="glass-card p-6 space-y-4">
          <div className="skeleton h-6 w-64" />
          <div className="skeleton h-32 w-full" />
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6 sm:space-y-8 animate-fade-in w-full min-w-0">
      <div>
        <h1 className="text-xl sm:text-2xl lg:text-3xl font-bold tracking-tight text-surface-50">Settings</h1>
        <p className="text-xs sm:text-sm text-surface-400 mt-1">Configure default search preferences and active job sources</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Search Preferences Section */}
        <div className="glass-card p-4 sm:p-6 space-y-5 w-full">
          <div className="flex items-center gap-2.5 border-b border-surface-800 pb-3">
            <Sliders className="w-4 h-4 text-brand-400" />
            <h2 className="text-xs sm:text-sm font-semibold text-surface-200 uppercase tracking-wider">Search Preferences</h2>
          </div>

          {/* Keywords */}
          <div>
            <label className="block text-xs sm:text-sm font-medium text-surface-300 mb-1.5">Keywords</label>
            <div className="flex flex-wrap gap-1.5 mb-2.5">
              {keywords.map((kw, i) => (
                <span key={i} className="badge-brand text-xs flex items-center gap-1.5 px-3 py-1">
                  {kw}
                  <button type="button" onClick={() => handleRemoveKeyword(i)} className="hover:text-danger">
                    <X className="w-3 h-3" />
                  </button>
                </span>
              ))}
              {keywords.length === 0 && (
                <span className="text-xs text-surface-500 italic">No default keywords configured</span>
              )}
            </div>
            <div className="flex gap-2">
              <input
                type="text"
                placeholder="Add keyword (e.g. Junior AI Developer)..."
                value={newKeyword}
                onChange={e => setNewKeyword(e.target.value)}
                onKeyDown={e => { if (e.key === 'Enter') { e.preventDefault(); handleAddKeyword(); } }}
                className="input flex-1 text-xs sm:text-sm"
              />
              <button type="button" onClick={() => handleAddKeyword()} className="btn-secondary btn-sm px-3">
                <Plus className="w-4 h-4" /> Add
              </button>
            </div>
          </div>

          {/* Locations */}
          <div>
            <label className="block text-xs sm:text-sm font-medium text-surface-300 mb-1.5">Preferred Locations</label>
            <div className="flex flex-wrap gap-1.5 mb-2.5">
              {locations.map((loc, i) => (
                <span key={i} className="badge-neutral text-xs flex items-center gap-1.5 px-3 py-1">
                  {loc}
                  <button type="button" onClick={() => handleRemoveLocation(i)} className="hover:text-danger">
                    <X className="w-3 h-3" />
                  </button>
                </span>
              ))}
              {locations.length === 0 && (
                <span className="text-xs text-surface-500 italic">No default locations configured</span>
              )}
            </div>
            <div className="flex gap-2">
              <input
                type="text"
                placeholder="Add location (e.g. Bangalore)..."
                value={newLocation}
                onChange={e => setNewLocation(e.target.value)}
                onKeyDown={e => { if (e.key === 'Enter') { e.preventDefault(); handleAddLocation(); } }}
                className="input flex-1 text-xs sm:text-sm"
              />
              <button type="button" onClick={() => handleAddLocation()} className="btn-secondary btn-sm px-3">
                <Plus className="w-4 h-4" /> Add
              </button>
            </div>
          </div>

          {/* Experience & Work Mode */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
            <div>
              <label className="block text-xs sm:text-sm font-medium text-surface-300 mb-1">Experience Level</label>
              <select value={experience} onChange={e => setExperience(e.target.value)} className="input w-full text-xs sm:text-sm">
                <option value="Fresher">Fresher (0-2 years)</option>
                <option value="Mid">Mid Level (2-5 years)</option>
                <option value="Senior">Senior (5+ years)</option>
              </select>
            </div>

            <div>
              <label className="block text-xs sm:text-sm font-medium text-surface-300 mb-1">Work Mode</label>
              <select value={remoteType} onChange={e => setRemoteType(e.target.value)} className="input w-full text-xs sm:text-sm">
                <option value="any">Any</option>
                <option value="remote">Remote</option>
                <option value="hybrid">Hybrid</option>
                <option value="onsite">On-site</option>
              </select>
            </div>
          </div>

          {/* Employment Types */}
          <div>
            <label className="block text-xs sm:text-sm font-medium text-surface-300 mb-2">Employment Types</label>
            <div className="flex flex-wrap gap-2">
              {EMPLOYMENT_OPTIONS.map((emp) => {
                const isSelected = employmentTypes.includes(emp);
                return (
                  <button
                    key={emp}
                    type="button"
                    onClick={() => toggleEmployment(emp)}
                    className={isSelected ? 'badge-brand cursor-pointer px-3 py-1.5 text-xs' : 'badge-neutral cursor-pointer px-3 py-1.5 text-xs'}
                  >
                    {emp}
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {/* Job Sources Section */}
        <div className="glass-card p-4 sm:p-6 space-y-4 w-full">
          <div className="flex items-center gap-2.5 border-b border-surface-800 pb-3">
            <Globe className="w-4 h-4 text-brand-400" />
            <h2 className="text-xs sm:text-sm font-semibold text-surface-200 uppercase tracking-wider">Job Sources</h2>
          </div>

          <p className="text-xs text-surface-400">Select which active job sources to include during multi-source job searches:</p>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {AVAILABLE_SOURCES.map((src) => {
              const isEnabled = enabledSources.includes(src.id);
              return (
                <label
                  key={src.id}
                  className={`flex items-center gap-3 p-3 rounded-xl border cursor-pointer transition-all ${
                    isEnabled
                      ? 'bg-brand-500/10 border-brand-500/40 text-surface-100 font-semibold'
                      : 'bg-surface-900/60 border-surface-800 text-surface-400'
                  }`}
                >
                  <input
                    type="checkbox"
                    checked={isEnabled}
                    onChange={() => toggleSource(src.id)}
                    className="rounded border-surface-700 bg-surface-800 text-brand-500 focus:ring-brand-500 w-4 h-4"
                  />
                  <span className="text-xs sm:text-sm capitalize">{src.label}</span>
                </label>
              );
            })}
          </div>
        </div>

        {/* Submit */}
        <div className="flex justify-end">
          <button
            type="submit"
            disabled={isPending}
            className="btn-primary w-full sm:w-auto justify-center min-h-[44px] px-6"
          >
            {isPending ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Save className="w-4 h-4 mr-2" />}
            Save Settings
          </button>
        </div>
      </form>
    </div>
  );
}
