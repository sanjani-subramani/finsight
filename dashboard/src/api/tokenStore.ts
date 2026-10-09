// Token storage: an in-memory copy (read on every request, zero latency)
// backed by sessionStorage rather than localStorage. sessionStorage
// clears when the tab/browser closes, which shrinks the window a stolen
// token is actually useful for -- the right tradeoff for an ops
// dashboard that's routinely used on shared or kiosk-style machines,
// where "survives a browser restart" is a liability, not a convenience.

const ACCESS_TOKEN_KEY = 'fs_access_token'
const REFRESH_TOKEN_KEY = 'fs_refresh_token'

let accessToken: string | null = null
let refreshToken: string | null = null
let initialized = false

function ensureInitialized(): void {
  if (initialized) return
  initialized = true
  try {
    accessToken = sessionStorage.getItem(ACCESS_TOKEN_KEY)
    refreshToken = sessionStorage.getItem(REFRESH_TOKEN_KEY)
  } catch {
    // sessionStorage can throw in a locked-down browsing context (e.g. a
    // sandboxed iframe); fall back to memory-only for that tab.
    accessToken = null
    refreshToken = null
  }
}

export const tokenStore = {
  getAccessToken(): string | null {
    ensureInitialized()
    return accessToken
  },
  getRefreshToken(): string | null {
    ensureInitialized()
    return refreshToken
  },
  setTokens(access: string, refresh: string): void {
    initialized = true
    accessToken = access
    refreshToken = refresh
    try {
      sessionStorage.setItem(ACCESS_TOKEN_KEY, access)
      sessionStorage.setItem(REFRESH_TOKEN_KEY, refresh)
    } catch {
      // Memory-only fallback is still correct for the lifetime of this tab.
    }
  },
  clear(): void {
    initialized = true
    accessToken = null
    refreshToken = null
    try {
      sessionStorage.removeItem(ACCESS_TOKEN_KEY)
      sessionStorage.removeItem(REFRESH_TOKEN_KEY)
    } catch {
      // ignore
    }
  },
}
