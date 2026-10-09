import { NavLink } from 'react-router-dom'
import type { ReactNode } from 'react'

/* ── SVG icon components (inline for zero bundle bloat) ── */
const icons: Record<string, ReactNode> = {
  overview: (
    <svg viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="7" rx="1" /><rect x="14" y="3" width="7" height="7" rx="1" /><rect x="3" y="14" width="7" height="7" rx="1" /><rect x="14" y="14" width="7" height="7" rx="1" /></svg>
  ),
  payments: (
    <svg viewBox="0 0 24 24"><rect x="2" y="5" width="20" height="14" rx="2" /><line x1="2" y1="10" x2="22" y2="10" /></svg>
  ),
  reconciliation: (
    <svg viewBox="0 0 24 24"><path d="M16 3h5v5" /><line x1="21" y1="3" x2="14" y2="10" /><path d="M8 21H3v-5" /><line x1="3" y1="21" x2="10" y2="14" /><line x1="3" y1="3" x2="21" y2="21" /></svg>
  ),
  dependencies: (
    <svg viewBox="0 0 24 24"><circle cx="12" cy="5" r="3" /><circle cx="5" cy="19" r="3" /><circle cx="19" cy="19" r="3" /><line x1="12" y1="8" x2="5" y2="16" /><line x1="12" y1="8" x2="19" y2="16" /></svg>
  ),
  compliance: (
    <svg viewBox="0 0 24 24"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" /></svg>
  ),
  threat: (
    <svg viewBox="0 0 24 24"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" /><line x1="12" y1="9" x2="12" y2="13" /><line x1="12" y1="17" x2="12.01" y2="17" /></svg>
  ),
  audit: (
    <svg viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" /><polyline points="14 2 14 8 20 8" /><line x1="16" y1="13" x2="8" y2="13" /><line x1="16" y1="17" x2="8" y2="17" /><polyline points="10 9 9 9 8 9" /></svg>
  ),
  system: (
    <svg viewBox="0 0 24 24"><rect x="2" y="3" width="20" height="14" rx="2" ry="2" /><line x1="8" y1="21" x2="16" y2="21" /><line x1="12" y1="17" x2="12" y2="21" /></svg>
  ),
}

interface NavSection {
  label: string
  items: { to: string; label: string; icon: string; end?: boolean }[]
}

const NAV_SECTIONS: NavSection[] = [
  {
    label: 'Operations',
    items: [
      { to: '/', label: 'Overview', icon: 'overview', end: true },
      { to: '/payments', label: 'Payments', icon: 'payments' },
      { to: '/reconciliation', label: 'Reconciliation', icon: 'reconciliation' },
    ],
  },
  {
    label: 'Infrastructure',
    items: [
      { to: '/dependencies', label: 'Dependencies', icon: 'dependencies' },
      { to: '/compliance', label: 'Compliance', icon: 'compliance' },
    ],
  },
  {
    label: 'Security',
    items: [
      { to: '/threats', label: 'Threat Intel', icon: 'threat' },
    ],
  },
  {
    label: 'System',
    items: [
      { to: '/audit', label: 'Audit Trail', icon: 'audit' },
      { to: '/system', label: 'System Health', icon: 'system' },
    ],
  },
]

export function Nav() {
  return (
    <>
      {NAV_SECTIONS.map((section) => (
        <div key={section.label} className="nav-section">
          <span className="nav-section__label">{section.label}</span>
          {section.items.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                'nav-link' + (isActive ? ' nav-link--active' : '')
              }
            >
              <span className="nav-link__icon">{icons[item.icon]}</span>
              <span className="nav-link__label">{item.label}</span>
            </NavLink>
          ))}
        </div>
      ))}
    </>
  )
}
