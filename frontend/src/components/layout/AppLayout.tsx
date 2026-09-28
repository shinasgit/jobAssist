import { Outlet, Link } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { MobileBottomNav } from './MobileBottomNav';
import { Zap, Settings } from 'lucide-react';

export function AppLayout() {
  return (
    <div className="flex flex-col md:flex-row h-screen overflow-hidden bg-surface-950 text-surface-100">
      {/* Desktop Sidebar */}
      <Sidebar />

      {/* Mobile Header Bar */}
      <header className="flex md:hidden items-center justify-between px-4 py-3 bg-surface-900/90 border-b border-surface-800 shrink-0 z-40">
        <Link to="/dashboard" className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-gradient-brand flex items-center justify-center shadow-glow-sm">
            <Zap className="w-3.5 h-3.5 text-white" />
          </div>
          <div>
            <span className="text-sm font-bold text-surface-50">JobPilot</span>
            <span className="block text-[10px] text-surface-400 -mt-0.5">Personal Finder</span>
          </div>
        </Link>

        <Link 
          to="/settings" 
          id="mobile-nav-settings"
          className="p-1.5 rounded-lg text-surface-400 hover:text-surface-100 hover:bg-surface-800 transition-colors"
        >
          <Settings className="w-5 h-5" />
        </Link>
      </header>

      {/* Main Page Area */}
      <main className="flex-1 overflow-y-auto w-full max-w-full overflow-x-hidden pb-20 md:pb-0">
        <div className="min-h-full p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto w-full animate-fade-in">
          <Outlet />
        </div>
      </main>

      {/* Mobile Bottom Navigation */}
      <MobileBottomNav />
    </div>
  );
}
