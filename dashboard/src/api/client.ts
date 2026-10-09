import axios, { AxiosError, type InternalAxiosRequestConfig } from 'axios'
import { tokenStore } from './tokenStore'

export const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? 'http://localhost:8000'

export const apiClient = axios.create({ baseURL: API_BASE_URL })

// A separate, un-intercepted client for the refresh call itself -- routing
// it through apiClient's own response interceptor would recurse (a failed
// refresh is itself a 401). Exported so tests can install a fake adapter
// on it directly, the same way they do for apiClient.
export const refreshClient = axios.create({ baseURL: API_BASE_URL })

let onAuthExpired: (() => void) | null = null
export function setOnAuthExpired(callback: () => void): void {
  onAuthExpired = callback
}

apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = tokenStore.getAccessToken()
  if (token) {
    config.headers.set('Authorization', `Bearer ${token}`)
  }
  return config
})

// SINGLE-FLIGHT REFRESH -- mirrors the Flutter app's AuthInterceptor
// (Step 13) exactly, and for the identical reason. If several requests
// fail with 401 at the same moment (e.g. a page fires 4 parallel
// queries right as the access token expires), each independently
// calling /auth/refresh would race to redeem the SAME refresh token.
// The backend's refresh-rotation reuse detection treats a second use of
// an already-rotated refresh token as a theft signal and revokes the
// entire token chain -- logging the user out even though nothing was
// actually stolen, just because two browser tabs' worth of requests
// each tried to refresh independently. This module-level promise makes
// every concurrent 401 await the ONE in-flight refresh instead of
// racing to start their own.
let refreshInFlight: Promise<string> | null = null

async function refreshAccessToken(): Promise<string> {
  if (refreshInFlight) return refreshInFlight

  refreshInFlight = (async () => {
    const refreshToken = tokenStore.getRefreshToken()
    if (!refreshToken) throw new Error('No refresh token available')
    const response = await refreshClient.post<{ access_token: string; refresh_token: string }>(
      '/auth/refresh',
      { refresh_token: refreshToken },
    )
    tokenStore.setTokens(response.data.access_token, response.data.refresh_token)
    return response.data.access_token
  })()

  try {
    return await refreshInFlight
  } finally {
    refreshInFlight = null
  }
}

interface RetriableConfig extends InternalAxiosRequestConfig {
  _retried?: boolean
}

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const original = error.config as RetriableConfig | undefined

    if (error.response?.status !== 401 || !original || original._retried) {
      throw error
    }
    // A failed call to the auth endpoints themselves is never retried
    // via refresh -- login/refresh/register returning 401 IS the
    // definitive answer, not something a token refresh could fix, and
    // retrying it risks a refresh loop.
    if (original.url?.startsWith('/auth/')) {
      throw error
    }

    original._retried = true
    try {
      const newAccessToken = await refreshAccessToken()
      original.headers.set('Authorization', `Bearer ${newAccessToken}`)
      return apiClient(original)
    } catch (refreshError) {
      tokenStore.clear()
      onAuthExpired?.()
      throw refreshError
    }
  },
)
