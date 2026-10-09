import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { adminApi, reportsApi } from '../api/admin'

export function useQueues() {
  return useQuery({
    queryKey: ['admin', 'queues'],
    queryFn: () => adminApi.getQueues(),
    refetchInterval: 5000,
  })
}

export function useDlq(limit = 50) {
  return useQuery({
    queryKey: ['admin', 'dlq', limit],
    queryFn: () => adminApi.getDlq(limit),
  })
}

export function useWorkerHealth() {
  return useQuery({
    queryKey: ['admin', 'workerHealth'],
    queryFn: () => adminApi.getWorkerHealth(),
    refetchInterval: 10000,
  })
}

export function usePipelineMetrics() {
  return useQuery({
    queryKey: ['reports', 'pipelineMetrics'],
    queryFn: () => reportsApi.getPipelineMetrics(),
    refetchInterval: 15000,
  })
}

export function useShadowReport() {
  return useQuery({
    queryKey: ['reports', 'shadowPrecision'],
    queryFn: () => reportsApi.getShadowReport(),
  })
}

export function useLoadTestReport() {
  return useQuery({
    queryKey: ['reports', 'loadTest'],
    queryFn: () => reportsApi.getLoadTestReport(),
    retry: false, // If there's no load test file, don't retry 404
  })
}

export function useReplayDlq() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (messageId: string) => adminApi.replayDlq(messageId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['admin', 'dlq'] })
      qc.invalidateQueries({ queryKey: ['admin', 'queues'] })
    },
  })
}

export function useDeleteDlq() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (messageId: string) => adminApi.deleteDlq(messageId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['admin', 'dlq'] }),
  })
}
