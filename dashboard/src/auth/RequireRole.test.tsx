import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { OrgAuthContext, type OrgAuthContextValue } from './OrgAuthContext'
import { RequireRole } from './RequireRole'
import type { OrgRole } from '../types/auth'

function withRole(role: OrgRole | null, children: React.ReactNode) {
  const value: OrgAuthContextValue = {
    user: null,
    orgs: [],
    currentOrgId: 'org-1',
    currentMembership: role ? { org_id: 'org-1', org_name: 'Acme', org_slug: 'acme', role } : null,
    currentRole: role,
    isAuthenticated: true,
    isLoading: false,
    login: async () => {},
    logout: () => {},
    switchOrg: () => {},
  }
  return <OrgAuthContext.Provider value={value}>{children}</OrgAuthContext.Provider>
}

describe('RequireRole', () => {
  it('hides content when the current role is not included', () => {
    render(withRole('viewer', <RequireRole roles={['owner']}>{<button>Delete</button>}</RequireRole>))
    expect(screen.queryByText('Delete')).not.toBeInTheDocument()
  })

  it('shows content when the current role is included', () => {
    render(withRole('owner', <RequireRole roles={['owner', 'ops_engineer']}>{<button>Delete</button>}</RequireRole>))
    expect(screen.getByText('Delete')).toBeInTheDocument()
  })

  it('mode="disable" renders the child disabled with an explanatory title instead of hiding it', () => {
    render(
      withRole('viewer', (
        <RequireRole roles={['owner']} mode="disable">
          <button>Delete</button>
        </RequireRole>
      )),
    )
    const button = screen.getByText('Delete') as HTMLButtonElement
    expect(button).toBeInTheDocument()
    expect(button).toBeDisabled()
    expect(button.title).toContain('owner')
  })
})
