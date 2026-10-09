import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { regimpactApi, type IngestRegulationPayload } from '../api/regimpact'

export function useRegulationRules(orgId: string | null, regulationId: string | null) {
  return useQuery({
    queryKey: ['regimpact', 'rules', orgId, regulationId],
    queryFn: () => regimpactApi.getRegulationRules(orgId as string, regulationId as string),
    enabled: !!orgId && !!regulationId,
  })
}

export function usePendingRules(orgId: string | null) {
  return useQuery({
    queryKey: ['regimpact', 'pending-rules', orgId],
    queryFn: () => regimpactApi.getPendingRules(orgId as string),
    enabled: !!orgId,
  })
}

export function useConfirmedRules(orgId: string | null) {
  return useQuery({
    queryKey: ['regimpact', 'confirmed-rules', orgId],
    queryFn: () => regimpactApi.getConfirmedRules(orgId as string),
    enabled: !!orgId,
  })
}

export function useImpactReports(orgId: string | null) {
  return useQuery({
    queryKey: ['regimpact', 'reports', orgId],
    queryFn: () => regimpactApi.listReports(orgId as string),
    enabled: !!orgId,
  })
}

export function useIngestRegulation(orgId: string | null) {
  return useMutation({
    mutationFn: (payload: IngestRegulationPayload) => regimpactApi.ingestRegulation(orgId as string, payload),
  })
}

/**
 * Reviewing (confirming or rejecting) a regulatory rule is deliberately
 * PESSIMISTIC, the opposite of Reconciliation's resolve mutation: a
 * confirmed rule immediately becomes eligible for run_impact_analysis
 * (Step 17's hard human-review gate), so the UI must show a success state
 * only once the server has actually recorded the decision -- there is no
 * safe "assume it worked" here.
 */
export function useReviewRule(orgId: string | null, regulationId: string | null = null) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ ruleId, decision, note }: { ruleId: string; decision: 'confirmed' | 'rejected'; note?: string }) =>
      regimpactApi.reviewRule(orgId as string, ruleId, decision, note),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['regimpact', 'rules', orgId, regulationId] })
      void queryClient.invalidateQueries({ queryKey: ['regimpact', 'pending-rules', orgId] })
      void queryClient.invalidateQueries({ queryKey: ['regimpact', 'confirmed-rules', orgId] })
    },
  })
}

export function useAnalyzeRule(orgId: string | null) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (ruleId: string) => regimpactApi.analyzeRule(orgId as string, ruleId),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['regimpact', 'reports', orgId] })
    },
  })
}
