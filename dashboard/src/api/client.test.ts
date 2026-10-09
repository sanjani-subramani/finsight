import type { AxiosHeaders, AxiosRequestConfig, AxiosResponse } from 'axios'
import { beforeEach, describe, expect, it } from 'vitest'
import { apiClient, refreshClient } from './client'
import { tokenStore } from './tokenStore'

function ok(config: AxiosRequestConfig, data: unknown): AxiosResponse {
  return { data, status: 200, statusText: 'OK', headers: {}, config: config as never }
}

function unauthorized(config: AxiosRequestConfig) {
  const error = new Error('Unauthorized') as Error & {
    isAxiosError: boolean
    response: AxiosResponse
    config: AxiosRequestConfig
  }
  error.isAxiosError = true
  error.config = config
  error.response = { data: {}, status: 401, statusText: 'Unauthorized', headers: {}, config: config as never }
  return error
}

describe('single-flight token refresh', () => {
  beforeEach(() => {
    tokenStore.setTokens('expired-access-token', 'valid-refresh-token')
  })

  it('concurrent 401s trigger exactly one call to /auth/refresh', async () => {
    let refreshCallCount = 0

    refreshClient.defaults.adapter = async (config) => {
      refreshCallCount += 1
      // A tiny delay so the three concurrent requests below all hit their
      // 401 and start waiting on the SAME in-flight refresh, rather than
      // the first one finishing before the second even starts.
      await new Promise((resolve) => setTimeout(resolve, 10))
      return ok(config, { access_token: 'new-access-token', refresh_token: 'new-refresh-token' })
    }

    apiClient.defaults.adapter = async (config) => {
      const authHeader = (config.headers as AxiosHeaders).get('Authorization')
      if (authHeader === 'Bearer expired-access-token') {
        throw unauthorized(config)
      }
      return ok(config, { ok: true, sawToken: authHeader })
    }

    const responses = await Promise.all([
      apiClient.get('/org/x/paytrace/health'),
      apiClient.get('/org/x/reconx/runs'),
      apiClient.get('/org/x/fingraph/graph'),
    ])

    // Without the single-flight guard, each of the 3 concurrent 401s
    // would fire its own /auth/refresh using the SAME (soon-to-be-stale)
    // refresh token -- the backend's rotation-reuse theft detection would
    // then revoke the whole chain and log the user out for no reason.
    expect(refreshCallCount).toBe(1)
    for (const response of responses) {
      expect(response.data.sawToken).toBe('Bearer new-access-token')
    }
    expect(tokenStore.getAccessToken()).toBe('new-access-token')
  })

  it('never attempts to refresh a 401 from the auth endpoints themselves', async () => {
    let refreshCallCount = 0
    refreshClient.defaults.adapter = async (config) => {
      refreshCallCount += 1
      return ok(config, {})
    }
    apiClient.defaults.adapter = async (config) => {
      throw unauthorized(config)
    }

    await expect(apiClient.post('/auth/login', {})).rejects.toBeTruthy()
    expect(refreshCallCount).toBe(0)
  })
})
