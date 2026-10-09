import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { fingraphApi, type AddEdgePayload, type AddNodePayload } from '../api/fingraph'

export function useGraph(orgId: string | null) {
  return useQuery({
    queryKey: ['fingraph', 'graph', orgId],
    queryFn: () => fingraphApi.getGraph(orgId as string),
    enabled: !!orgId,
  })
}

export function useCriticalNodes(orgId: string | null) {
  return useQuery({
    queryKey: ['fingraph', 'critical-nodes', orgId],
    queryFn: () => fingraphApi.getCriticalNodes(orgId as string),
    enabled: !!orgId,
  })
}

export function useSimulationHistory(orgId: string | null) {
  return useQuery({
    queryKey: ['fingraph', 'history', orgId],
    queryFn: () => fingraphApi.getHistory(orgId as string),
    enabled: !!orgId,
  })
}

export function useAddNode(orgId: string | null) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (payload: AddNodePayload) => fingraphApi.addNode(orgId as string, payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['fingraph', 'graph', orgId] })
      void queryClient.invalidateQueries({ queryKey: ['fingraph', 'critical-nodes', orgId] })
    },
  })
}

export function useAddEdge(orgId: string | null) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (payload: AddEdgePayload) => fingraphApi.addEdge(orgId as string, payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['fingraph', 'graph', orgId] })
      void queryClient.invalidateQueries({ queryKey: ['fingraph', 'critical-nodes', orgId] })
    },
  })
}

export function useSimulateFailure(orgId: string | null) {
  return useMutation({
    mutationFn: ({ nodeName, durationHours }: { nodeName: string; durationHours?: number }) =>
      fingraphApi.simulate(orgId as string, nodeName, durationHours),
  })
}
