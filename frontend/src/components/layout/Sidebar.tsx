import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard, Search, Briefcase, Bookmark, ClipboardList,
  Settings, Zap, ChevronRight, Building2, Rocket, Cpu, Globe
} from 'lucide-react';
import clsx from 'clsx';

const MAIN_NAV = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/find-jobs', icon: Search, label: 'Find Jobs' },
  { to: '/jobs', icon: Briefcase, label: 'All Jobs' },
];

const SOURCE_NAV = [
  { to: '/jobs?category=mnc', icon: Building2, label: '🏢 MNC Jobs' },
  { to: '/jobs?category=startup', icon: Rocket, label: '🚀 Startup Jobs' },
  { to: '/jobs?category=it-tech', icon: Cpu, label: '💻 IT & Tech Jobs' },
  { to: '/jobs?category=remote', icon: Globe, label: '🌐 Remote Jobs' },
];

const COMING_SOON_NAV = [
  { to: '/saved-jobs', icon: Bookmark, label: 'Saved Jobs', badge: 'Soon' },
  { to: '/applications', icon: ClipboardList, label: 'Applications', badge: 'Soon' },
  { to: '/settings', icon: Settings, label: 'Settings' },
];

export function Sidebar() {
  return (
    <aside className="hidden md:flex flex-col w-64 h-screen bg-surface-900/80 backdrop-blur-xl border-r border-surface-800 px-3 py-5 shrink-0 overflow-y-auto">
      {/* Logo */}
      <div className="flex items-center gap-2.5 px-3 mb-6 shrink-0">
        <div className="w-8 h-8 rounded-xl bg-gradient-brand flex items-center justify-center shadow-glow-sm">
          <Zap className="w-4 h-4 text-white" />
        </div>
        <div>
          <span className="text-sm font-bold text-surface-50">JobPilot</span>
          <span className="block text-[11px] text-surface-400">Career Page Collector</span>
        </div>
      </div>

      {/* Main Navigation */}
      <nav className="flex-1 space-y-5">
        <div className="space-y-1">
          {MAIN_NAV.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                clsx(isActive ? 'nav-link-active' : 'nav-link-inactive')
              }
            >
              <Icon className="w-4 h-4 shrink-0" />
              <span className="truncate">{label}</span>
              <ChevronRight className="w-3 h-3 ml-auto opacity-0 group-hover:opacity-100 transition-opacity" />
            </NavLink>
          ))}
        </div>

        {/* Job Sources Section */}
        <div className="space-y-1 pt-2">
          <p className="px-3 text-[11px] font-semibold text-surface-400 uppercase tracking-wider mb-2">Job Sources</p>
          {SOURCE_NAV.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                clsx(isActive ? 'nav-link-active' : 'nav-link-inactive')
              }
            >
              <span className="truncate text-xs font-medium">{label}</span>
            </NavLink>
          ))}
        </div>

        {/* Coming Soon & Settings Section */}
        <div className="space-y-1 pt-2 border-t border-surface-800/60">
          {COMING_SOON_NAV.map(({ to, icon: Icon, label, badge }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                clsx(isActive ? 'nav-link-active' : 'nav-link-inactive')
              }
            >
              <Icon className="w-4 h-4 shrink-0" />
              <span className="truncate">{label}</span>
              {badge && (
                <span className="ml-auto text-[10px] font-semibold px-2 py-0.5 rounded-full bg-surface-800 text-surface-400 border border-surface-700">
                  {badge}
                </span>
              )}
            </NavLink>
          ))}
        </div>
      </nav>

      {/* Footer */}
      <div className="mt-4 pt-4 border-t border-surface-800 px-3 text-[11px] text-surface-500 shrink-0">
        JobPilot Aggregator v1.0
      </div>
    </aside>
  );
}
