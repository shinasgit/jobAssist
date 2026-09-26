import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard, Search, Briefcase, Bookmark, ClipboardList,
  Settings, Zap, ChevronRight,
} from 'lucide-react';
import clsx from 'clsx';

const NAV_ITEMS = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/find-jobs', icon: Search, label: 'Find Jobs' },
  { to: '/jobs', icon: Briefcase, label: 'Jobs' },
  { to: '/saved-jobs', icon: Bookmark, label: 'Saved Jobs' },
  { to: '/applications', icon: ClipboardList, label: 'Applications' },
  { to: '/settings', icon: Settings, label: 'Settings' },
];

export function Sidebar() {
  return (
    <aside className="flex flex-col w-64 h-screen bg-surface-900/80 backdrop-blur-xl border-r border-surface-800 px-3 py-5 shrink-0">
      {/* Logo */}
      <div className="flex items-center gap-2.5 px-3 mb-8">
        <div className="w-8 h-8 rounded-xl bg-gradient-brand flex items-center justify-center shadow-glow-sm">
          <Zap className="w-4 h-4 text-white" />
        </div>
        <div>
          <span className="text-sm font-bold text-surface-50">Job Finder</span>
          <span className="block text-xs text-surface-500">Personal</span>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1">
        {NAV_ITEMS.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              clsx(isActive ? 'nav-link-active' : 'nav-link-inactive')
            }
            id={`nav-${label.toLowerCase().replace(/\s+/g, '-')}`}
          >
            <Icon className="w-4 h-4 shrink-0" />
            <span>{label}</span>
            <ChevronRight className="w-3 h-3 ml-auto opacity-0 group-hover:opacity-100 transition-opacity" />
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="mt-4 pt-4 border-t border-surface-800 px-3 text-xs text-surface-500">
        Personal Use Only
      </div>
    </aside>
  );
}
