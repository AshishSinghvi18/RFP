import { Menu } from 'lucide-react';
import { ReactNode, useMemo, useState } from 'react';
import { useLocation } from 'react-router-dom';

import Sidebar from '@/components/layout/Sidebar';
import { useAuth } from '@/store/AuthContext';

interface LayoutProps {
  children: ReactNode;
}

const titleMap: Record<string, string> = {
  '/': 'Dashboard',
  '/opportunities': 'Opportunities',
  '/search': 'Search',
  '/copilot': 'AI Copilot',
  '/reports': 'Reports',
  '/alerts': 'Alerts',
  '/sources': 'Sources',
  '/admin': 'Admin',
};

const Layout = ({ children }: LayoutProps) => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const { pathname } = useLocation();
  const { user } = useAuth();

  const pageTitle = useMemo(() => {
    const directMatch = Object.entries(titleMap).find(([route]) => route !== '/' && pathname.startsWith(route));

    if (directMatch) {
      return directMatch[1];
    }

    return titleMap[pathname] ?? 'RFP Intelligence';
  }, [pathname]);

  const initials = user?.full_name
    ?.split(' ')
    .map((part) => part[0])
    .join('')
    .slice(0, 2)
    .toUpperCase();

  return (
    <div className="min-h-screen bg-slate-50">
      <Sidebar isOpen={isSidebarOpen} onClose={() => setIsSidebarOpen(false)} />

      <div className="lg:pl-64">
        <header className="sticky top-0 z-20 border-b border-slate-200 bg-white/90 backdrop-blur">
          <div className="flex items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
            <div className="flex items-center gap-3">
              <button
                type="button"
                onClick={() => setIsSidebarOpen(true)}
                className="rounded-xl border border-slate-200 p-2 text-slate-600 shadow-sm transition hover:bg-slate-50 lg:hidden"
              >
                <Menu className="h-5 w-5" />
              </button>
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Workspace</p>
                <h2 className="text-2xl font-semibold text-slate-900">{pageTitle}</h2>
              </div>
            </div>

            <div className="flex items-center gap-3 rounded-full border border-slate-200 bg-white px-3 py-2 shadow-sm">
              <div className="hidden text-right sm:block">
                <p className="text-sm font-semibold text-slate-900">{user?.full_name ?? 'Analyst'}</p>
                <p className="text-xs text-slate-500">{user?.role ?? 'viewer'}</p>
              </div>
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-blue-600 text-sm font-semibold text-white">
                {initials || 'RI'}
              </div>
            </div>
          </div>
        </header>

        <main className="px-4 py-6 sm:px-6 lg:px-8">{children}</main>
      </div>
    </div>
  );
};

export default Layout;
