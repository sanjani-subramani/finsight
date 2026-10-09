import { useState } from 'react'
import { Outlet } from 'react-router-dom'
import { useOrgAuth } from '../../auth/useOrgAuth'
import { Nav } from './Nav'
import { OrgSwitcher } from './OrgSwitcher'
import './Shell.css'

const ROLE_LABELS: Record<string, string> = {
  owner: 'Owner',
  ops_engineer: 'Ops Engineer',
  recon_analyst: 'Recon Analyst',
  viewer: 'Viewer',
}

export function Shell() {
  const { user, currentRole, logout } = useOrgAuth()
  const [collapsed, setCollapsed] = useState(false)

  const initials = user?.email
    ? user.email.substring(0, 2).toUpperCase()
    : '??'

  return (
    <div className={`app-shell${collapsed ? ' app-shell--collapsed' : ''}`}>
      <aside className={`app-sidebar${collapsed ? ' app-sidebar--collapsed' : ''}`}>
        <div className="app-sidebar__brand">
          <div className="app-sidebar__logo">FS</div>
          <span className="app-sidebar__title">FinSentinel</span>
        </div>

        <div className="app-sidebar__nav">
          <Nav />
        </div>

        <button
          className="sidebar-toggle"
          onClick={() => setCollapsed((c) => !c)}
          aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polyline points="15 18 9 12 15 6" />
          </svg>
        </button>

        <div className="app-sidebar__footer">
          <OrgSwitcher />
          <div className="sidebar-user">
            <div className="sidebar-user__avatar">{initials}</div>
            <div className="sidebar-user__info">
              <div className="sidebar-user__email">{user?.email}</div>
              {currentRole && (
                <span className="sidebar-user__role" data-testid="current-role">
                  {ROLE_LABELS[currentRole] ?? currentRole}
                </span>
              )}
            </div>
            <button
              type="button"
              className="sidebar-user__logout"
              onClick={logout}
              title="Log out"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4" />
                <polyline points="16 17 21 12 16 7" />
                <line x1="21" y1="12" x2="9" y2="12" />
              </svg>
            </button>
          </div>
        </div>
      </aside>

      <main className="app-main">
        <Outlet />
      </main>
    </div>
  )
}
