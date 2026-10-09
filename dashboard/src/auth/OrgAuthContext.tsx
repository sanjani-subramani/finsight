import { createContext, useCallback, useEffect, useMemo, useState, type ReactNode } from 'react'
import { authApi } from '../api/auth'
import { setOnAuthExpired } from '../api/client'
import { tokenStore } from '../api/tokenStore'
import type { OrgMembershipResponse, OrgRole, UserResponse } from '../types/auth'

const CURRENT_ORG_KEY = 'fs_current_org_id'

export interface OrgAuthContextValue {
  user: UserResponse | null
  orgs: OrgMembershipResponse[]
  currentOrgId: string | null
  currentMembership: OrgMembershipResponse | null
  currentRole: OrgRole | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  switchOrg: (orgId: string) => void
}

export const OrgAuthContext = createContext<OrgAuthContextValue | null>(null)

export function OrgAuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserResponse | null>(null)
  const [orgs, setOrgs] = useState<OrgMembershipResponse[]>([])
  const [currentOrgId, setCurrentOrgId] = useState<string | null>(() => {
    try {
      return sessionStorage.getItem(CURRENT_ORG_KEY)
    } catch {
      return null
    }
  })
  const [isLoading, setIsLoading] = useState(true)

  const clearSession = useCallback(() => {
    tokenStore.clear()
    setUser(null)
    setOrgs([])
    setCurrentOrgId(null)
    try {
      sessionStorage.removeItem(CURRENT_ORG_KEY)
    } catch {
      // ignore
    }
  }, [])

  useEffect(() => {
    // If a refresh ultimately fails (no valid refresh token left), the
    // api client tells us so it can drop back to the login screen rather
    // than leaving the UI in a half-authenticated state.
    setOnAuthExpired(clearSession)
  }, [clearSession])

  useEffect(() => {
    async function hydrate() {
      if (!tokenStore.getAccessToken()) {
        setIsLoading(false)
        return
      }
      try {
        const [me, myOrgs] = await Promise.all([authApi.me(), authApi.myOrgs()])
        setUser(me)
        setOrgs(myOrgs)
        setCurrentOrgId((prev) => prev ?? myOrgs[0]?.org_id ?? null)
      } catch {
        clearSession()
      } finally {
        setIsLoading(false)
      }
    }
    void hydrate()
  }, [clearSession])

  const login = useCallback(async (email: string, password: string) => {
    const tokens = await authApi.login(email, password)
    tokenStore.setTokens(tokens.access_token, tokens.refresh_token)
    const [me, myOrgs] = await Promise.all([authApi.me(), authApi.myOrgs()])
    setUser(me)
    setOrgs(myOrgs)
    setCurrentOrgId(myOrgs[0]?.org_id ?? null)
  }, [])

  const logout = useCallback(() => {
    const refreshToken = tokenStore.getRefreshToken()
    if (refreshToken) {
      authApi.logout(refreshToken).catch(() => {
        // Best-effort server-side revocation; the local session is
        // cleared either way below.
      })
    }
    clearSession()
  }, [clearSession])

  const switchOrg = useCallback((orgId: string) => {
    setCurrentOrgId(orgId)
    try {
      sessionStorage.setItem(CURRENT_ORG_KEY, orgId)
    } catch {
      // ignore
    }
  }, [])

  const currentMembership = useMemo(
    () => orgs.find((o) => o.org_id === currentOrgId) ?? null,
    [orgs, currentOrgId],
  )

  const value: OrgAuthContextValue = {
    user,
    orgs,
    currentOrgId,
    currentMembership,
    currentRole: currentMembership?.role ?? null,
    isAuthenticated: user !== null,
    isLoading,
    login,
    logout,
    switchOrg,
  }

  return <OrgAuthContext.Provider value={value}>{children}</OrgAuthContext.Provider>
}
