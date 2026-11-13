import { useEffect, useState } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import Icon from '../ui/Icon';
import SideNav, { Brand } from './SideNav';

export default function Shell() {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const { pathname } = useLocation();

  // Jump to the top on every route change, like a regular page load would.
  useEffect(() => {
    window.scrollTo(0, 0);
  }, [pathname]);

  return (
    <div className="shell">
      <header className="mobile-bar">
        <Brand />
        <button
          type="button"
          className="icon-button"
          aria-label={drawerOpen ? 'Close navigation' : 'Open navigation'}
          aria-expanded={drawerOpen}
          onClick={() => setDrawerOpen((v) => !v)}
        >
          <Icon name={drawerOpen ? 'close' : 'menu'} size={22} />
        </button>
      </header>

      <SideNav open={drawerOpen} onNavigate={() => setDrawerOpen(false)} />
      {drawerOpen && <div className="scrim" onClick={() => setDrawerOpen(false)} />}

      <main className="stage">
        <Outlet />
      </main>
    </div>
  );
}
