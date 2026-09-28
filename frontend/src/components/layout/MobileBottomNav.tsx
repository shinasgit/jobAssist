import { NavLink, useLocation } from 'react-router-dom';
import { LayoutDashboard, Sparkles, Briefcase, Settings } from 'lucide-react';
import clsx from 'clsx';

const MOBILE_NAV_ITEMS = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Home' },
  { to: '/find-jobs', icon: Sparkles, label: 'Search' },
  { to: '/jobs', icon: Briefcase, label: 'Jobs' },
  { to: '/settings', icon: Settings, label: 'Settings' },
];

export function MobileBottomNav() {
  const location = useLocation();

  return (
    <nav 
      aria-label="Mobile Bottom Navigation"
      className="md:hidden fixed bottom-0 left-0 right-0 z-50 bg-surface-900/95 backdrop-blur-md border-t border-surface-800/80 px-1 py-1.5 shadow-2xl safe-area-pb"
    >
      <div className="flex items-center justify-around max-w-md mx-auto">
        {MOBILE_NAV_ITEMS.map(({ to, icon: Icon, label }) => {
          const isActive = location.pathname === to || (to === '/dashboard' && location.pathname === '/');

          return (
            <NavLink
              key={to}
              to={to}
              id={`mobile-nav-${label.toLowerCase()}`}
              className={clsx(
                'flex flex-col items-center justify-center min-h-[44px] px-4 py-1 rounded-xl transition-all duration-150 text-center select-none',
                isActive
                  ? 'text-brand-400 font-semibold bg-brand-500/10 scale-105'
                  : 'text-surface-400 hover:text-surface-200 active:scale-95'
              )}
            >
              <Icon className={clsx('w-5 h-5 shrink-0 transition-transform', isActive && 'stroke-[2.5px]')} />
              <span className="text-[10px] tracking-tight mt-0.5">{label}</span>
            </NavLink>
          );
        })}
      </div>
    </nav>
  );
}
