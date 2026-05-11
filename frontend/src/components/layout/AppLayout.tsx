import { Outlet } from 'react-router-dom';
import { MobileNav } from './MobileNav';
import { RightRail } from './RightRail';
import { Sidebar } from './Sidebar';

export function AppLayout() {
  return (
    <div className="app-shell">
      <Sidebar />
      <main className="main-column">
        <Outlet />
      </main>
      <RightRail />
      <MobileNav />
    </div>
  );
}
