import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { threatApi } from '../api/threat'

export function useThreatList() {
  return useQuery({
    queryKey: ['threats'],
    queryFn: () => threatApi.listThreats(),
  })
}

export function useThreatDetail(threatId: string | null) {
  return useQuery({
    queryKey: ['threat', threatId],
    queryFn: () => threatApi.getThreat(threatId!),
    enabled: !!threatId,
  })
}

export function useAnalyzeSms() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (body: string) => threatApi.analyzeSms(body),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['threats'] }),
  })
}

export function useAnalyzeUrl() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (url: string) => threatApi.analyzeUrl(url),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['threats'] }),
  })
}

export function useAnalyzeQr() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (file: File) => threatApi.analyzeQr(file),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['threats'] }),
  })
}

export function useAnalyzeCall() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (file: File) => threatApi.analyzeCall(file),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['threats'] }),
  })
}
