import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { act, renderHook, waitFor } from '@testing-library/react'
import type { ReactNode } from 'react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { reconxApi } from '../api/reconx'
import { useResolveReconResult } from './useReconx'
import type { ReconRunResult } from '../types/reconx'

vi.mock('../api/reconx', () => ({
  reconxApi: {
    resolve: vi.fn(),
  },
}))

const ORG_ID = 'org-1'
const RUN_ID = 'run-1'
const QUERY_KEY = ['reconx', 'run', ORG_ID, RUN_ID]

function seedRun(): ReconRunResult {
  return {
    summary: {
      run_id: RUN_ID,
      period_start: '2026-01-01T00:00:00Z',
      period_end: '2026-01-02T00:00:00Z',
      total_records: 1,
      matched: 0,
      missing: 1,
      duplicates: 0,
      amount_mismatches: 0,
      timing_differences: 0,
      unresolved: 0,
      status: 'completed',
      duration_ms: 10,
      created_at: '2026-01-02T00:00:00Z',
    },
    results: [
      {
        result_id: 'result-1',
        run_id: RUN_ID,
        transaction_ref: 'TX1',
        status: 'missing_in_bank',
        internal_amount: '100.00',
        gateway_amount: '100.00',
        bank_amount: null,
        probable_cause: 'settlement delay',
        cause_confidence: 0.7,
        evidence: [],
        resolved: false,
        resolved_by: null,
        resolution_note: null,
      },
    ],
  }
}

describe('useResolveReconResult (optimistic update)', () => {
  let queryClient: QueryClient
  let wrapper: ({ children }: { children: ReactNode }) => React.JSX.Element

  beforeEach(() => {
    queryClient = new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } })
    queryClient.setQueryData(QUERY_KEY, seedRun())
    wrapper = ({ children }) => <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  })

  afterEach(() => {
    vi.resetAllMocks()
  })

  it('marks the row resolved immediately, before the server responds', async () => {
    let resolveServerCall: (() => void) | undefined
    vi.mocked(reconxApi.resolve).mockImplementation(
      () =>
        new Promise((resolve) => {
          resolveServerCall = () =>
            resolve({ ...seedRun().results[0], resolved: true, resolution_note: 'Confirmed with bank' })
        }),
    )

    const { result } = renderHook(() => useResolveReconResult(ORG_ID, RUN_ID), { wrapper })

    act(() => {
      result.current.mutate({ resultId: 'result-1', note: 'Confirmed with bank' })
    })

    // Optimistic: resolved=true shows up in the cache immediately, well
    // before the mocked server call has been allowed to complete.
    await waitFor(() => {
      const cached = queryClient.getQueryData<ReconRunResult>(QUERY_KEY)
      expect(cached?.results[0].resolved).toBe(true)
    })

    resolveServerCall?.()
    await waitFor(() => expect(result.current.isSuccess).toBe(true))
  })

  it('rolls back to unresolved when the server rejects the request', async () => {
    // Controllable rejection (rather than mockRejectedValue, which settles
    // on the very next microtask) so the test can observe the optimistic
    // "resolved: true" state BEFORE forcing the rollback, instead of
    // racing a `waitFor` against a round trip fast enough to complete
    // before the first poll.
    let rejectServerCall: ((err: Error) => void) | undefined
    vi.mocked(reconxApi.resolve).mockImplementation(
      () =>
        new Promise((_resolve, reject) => {
          rejectServerCall = reject
        }),
    )

    const { result } = renderHook(() => useResolveReconResult(ORG_ID, RUN_ID), { wrapper })

    act(() => {
      result.current.mutate({ resultId: 'result-1', note: 'Confirmed with bank' })
    })

    await waitFor(() => {
      const cached = queryClient.getQueryData<ReconRunResult>(QUERY_KEY)
      expect(cached?.results[0].resolved).toBe(true)
    })

    act(() => {
      rejectServerCall?.(new Error('server rejected'))
    })

    await waitFor(() => expect(result.current.isError).toBe(true))

    const cached = queryClient.getQueryData<ReconRunResult>(QUERY_KEY)
    expect(cached?.results[0].resolved).toBe(false)
    expect(cached?.results[0].resolution_note).toBeNull()
  })
})
