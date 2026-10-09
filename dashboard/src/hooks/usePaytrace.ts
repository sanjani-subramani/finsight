import { useQuery } from '@tanstack/react-query'
import { paytraceApi } from '../api/paytrace'
import type { TransactionSearchFilters } from '../types/paytrace'

export function usePaymentHealth(orgId: string | null) {
  return useQuery({
    queryKey: ['paytrace', 'health', orgId],
    queryFn: () => paytraceApi.getHealth(orgId as string),
    enabled: !!orgId,
  })
}

export function useProviderStats(orgId: string | null) {
  return useQuery({
    queryKey: ['paytrace', 'providers', orgId],
    queryFn: () => paytraceApi.getProviders(orgId as string),
    enabled: !!orgId,
  })
}

export function useProviderAlerts(orgId: string | null) {
  return useQuery({
    queryKey: ['paytrace', 'alerts', orgId],
    queryFn: () => paytraceApi.getAlerts(orgId as string),
    enabled: !!orgId,
    refetchInterval: 60_000,
  })
}

export function useTransactionSearch(orgId: string | null, filters: TransactionSearchFilters) {
  return useQuery({
    queryKey: ['paytrace', 'transactions', orgId, filters],
    queryFn: () => paytraceApi.searchTransactions(orgId as string, filters),
    enabled: !!orgId,
  })
}

export function useTransactionDetail(orgId: string | null, ref: string | null) {
  return useQuery({
    queryKey: ['paytrace', 'transaction', orgId, ref],
    queryFn: () => paytraceApi.getTransaction(orgId as string, ref as string),
    enabled: !!orgId && !!ref,
  })
}
