import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { reconxApi } from '../api/reconx'
import type { ReconRunRequest } from '../types/reconx'

export function useReconRuns(orgId: string | null) {
  return useQuery({
    queryKey: ['reconx', 'runs', orgId],
    queryFn: () => reconxApi.listRuns(orgId as string),
    enabled: !!orgId,
  })
}

export function useReconRun(orgId: string | null, runId: string | null) {
  return useQuery({
    queryKey: ['reconx', 'run', orgId, runId],
    queryFn: () => reconxApi.getRun(orgId as string, runId as string),
    enabled: !!orgId && !!runId,
  })
}

export function useCreateReconRun(orgId: string | null) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (payload: ReconRunRequest) => reconxApi.createRun(orgId as string, payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['reconx', 'runs', orgId] })
    },
  })
}

/**
 * Resolve is a good fit for an optimistic update: the action is
 * reversible (a resolution note can be corrected later) and low-stakes
 * (it never moves money or changes a financial amount) -- unlike
 * anything in Compliance, where a wrong "confirmed" status could drive a
 * real regulatory mapping. The UI marks the row resolved immediately and
 * rolls back to the previous cache snapshot if the server rejects it.
 */
export function useResolveReconResult(orgId: string | null, runId: string | null) {
  const queryClient = useQueryClient()
  const queryKey = ['reconx', 'run', orgId, runId]

  return useMutation({
    mutationFn: ({ resultId, note }: { resultId: string; note: string }) =>
      reconxApi.resolve(orgId as string, runId as string, resultId, note),
    onMutate: async ({ resultId, note }) => {
      await queryClient.cancelQueries({ queryKey })
      const previous = queryClient.getQueryData(queryKey)
      queryClient.setQueryData(queryKey, (old: import('../types/reconx').ReconRunResult | undefined) => {
        if (!old) return old
        return {
          ...old,
          results: old.results.map((r) =>
            r.result_id === resultId ? { ...r, resolved: true, resolution_note: note } : r,
          ),
        }
      })
      return { previous }
    },
    onError: (_err, _vars, context) => {
      if (context?.previous) {
        queryClient.setQueryData(queryKey, context.previous)
      }
    },
    onSettled: () => {
      void queryClient.invalidateQueries({ queryKey })
    },
  })
}
