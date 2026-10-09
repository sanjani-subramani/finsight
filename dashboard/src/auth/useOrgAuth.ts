import { useContext } from 'react'
import { OrgAuthContext, type OrgAuthContextValue } from './OrgAuthContext'

export function useOrgAuth(): OrgAuthContextValue {
  const ctx = useContext(OrgAuthContext)
  if (!ctx) throw new Error('useOrgAuth must be used within an OrgAuthProvider')
  return ctx
}
