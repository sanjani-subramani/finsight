import type { OrgRole } from '../types/auth'
import { useOrgAuth } from './useOrgAuth'

/** The signed-in user's role in the currently-selected org, or null if
 * they don't belong to one (not yet loaded, or no org selected). */
export function useRole(): OrgRole | null {
  return useOrgAuth().currentRole
}

export function hasRole(role: OrgRole | null, allowed: OrgRole[]): boolean {
  return role !== null && allowed.includes(role)
}
