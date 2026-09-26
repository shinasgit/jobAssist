import { useState } from 'react';
import { User, Lock, Settings as SettingsIcon } from 'lucide-react';
import toast from 'react-hot-toast';

export default function Settings() {
  const [name, setName] = useState('Shinas S');
  const [email, setEmail] = useState('admin@local');

  function handleSave(e: React.FormEvent) {
    e.preventDefault();
    toast.success('Preferences saved locally');
  }

  return (
    <div className="max-w-2xl space-y-8">
      <div>
        <h1 className="page-title">Settings</h1>
        <p className="page-subtitle mt-1">Manage your local preferences</p>
      </div>

      <div className="glass-card p-6 space-y-4">
        <div className="flex items-center gap-3 mb-4">
          <SettingsIcon className="w-4 h-4 text-brand-400" />
          <h2 className="text-sm font-semibold text-surface-200">Local Profile</h2>
        </div>

        <form onSubmit={handleSave} className="space-y-4">
          <div>
            <label htmlFor="settings-name" className="label">Name</label>
            <input
              id="settings-name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="input"
            />
          </div>

          <div>
            <label className="label">Email</label>
            <input
              type="email"
              value={email}
              disabled
              className="input opacity-60 cursor-not-allowed"
            />
            <p className="text-xs text-surface-500 mt-1">Email is disabled for personal local app</p>
          </div>

          <button
            type="submit"
            className="btn-primary"
          >
            Save Preferences
          </button>
        </form>
      </div>
    </div>
  );
}
