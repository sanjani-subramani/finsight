import { Children, cloneElement, isValidElement, type ReactElement, type ReactNode } from 'react'
import type { OrgRole } from '../types/auth'
import { useRole } from './useRole'

export interface RequireRoleProps {
  roles: OrgRole[]
  children: ReactNode
  /** 'hide' (default): render nothing when the current role doesn't
   * qualify -- appropriate for whole sections (a nav item, a form) that
   * would just be confusing to show at all. 'disable': render the child
   * element disabled with a tooltip explaining why -- appropriate for a
   * single action worth showing-but-disabled, so a viewer understands
   * the capability exists and who to ask, rather than wondering why a
   * button they'd expect is simply missing. */
  mode?: 'hide' | 'disable'
  disabledReason?: string
}

/**
 * UX-ONLY GATE. This is a courtesy that keeps the interface honest about
 * what the current user can do here -- it is NOT the authorization
 * boundary. The real enforcement is the backend's require_roles
 * dependency (app.platform.deps, Step 2): every org-scoped endpoint
 * checks OrgMembership.role server-side on every single request,
 * completely independent of anything this component renders. Hiding or
 * disabling a button here only prevents confusion for a legitimate user
 * looking at a role they don't currently have -- a user who opens
 * devtools and calls the API directly is stopped by the backend check,
 * not by this component. Never treat frontend RBAC as security.
 */
export function RequireRole({ roles, children, mode = 'hide', disabledReason }: RequireRoleProps) {
  const role = useRole()
  const allowed = role !== null && roles.includes(role)

  if (allowed) return <>{children}</>
  if (mode === 'hide') return null

  const child = Children.only(children)
  if (!isValidElement(child)) return null

  const reason = disabledReason ?? `Requires one of: ${roles.join(', ')}`
  return cloneElement(child as ReactElement<{ disabled?: boolean; title?: string }>, {
    disabled: true,
    title: reason,
  })
}
