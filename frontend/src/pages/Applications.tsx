import { Link } from 'react-router-dom';
import { ClipboardList, Search } from 'lucide-react';

export default function Applications() {
  return (
    <div className="max-w-3xl mx-auto space-y-6 sm:space-y-8 animate-fade-in w-full min-w-0">
      <div>
        <h1 className="text-xl sm:text-2xl lg:text-3xl font-bold tracking-tight text-surface-50">Applications</h1>
        <p className="text-xs sm:text-sm text-surface-400 mt-1">Application Tracker Feature</p>
      </div>

      <div className="glass-card p-8 sm:p-12 text-center flex flex-col items-center justify-center border-brand-500/20 bg-brand-500/5">
        <div className="w-16 h-16 rounded-2xl bg-gradient-brand flex items-center justify-center text-white mb-4 shadow-glow-sm">
          <ClipboardList className="w-8 h-8" />
        </div>
        <span className="badge-brand text-xs px-3 py-1 font-semibold uppercase tracking-wider mb-2">Coming Soon</span>
        <h2 className="text-lg sm:text-xl font-bold text-surface-100 mb-2">Application Tracker in Development</h2>
        <p className="text-surface-400 text-xs sm:text-sm max-w-md mx-auto mb-6 leading-relaxed">
          The Application Tracker feature is currently scheduled for future release. Explore and apply to active positions directly via their original job listings.
        </p>
        <Link to="/find-jobs" className="btn-primary min-h-[44px]">
          <Search className="w-4 h-4 mr-2" />
          Find Jobs Now
        </Link>
      </div>
    </div>
  );
}
