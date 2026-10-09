import { apiClient } from './client'
import type {
  PaymentHealth,
  ProviderAlert,
  ProviderStats,
  TransactionDetail,
  TransactionSearchFilters,
  TransactionSearchResult,
} from '../types/paytrace'

export const paytraceApi = {
  async searchTransactions(orgId: string, filters: TransactionSearchFilters): Promise<TransactionSearchResult> {
    const { data } = await apiClient.get<TransactionSearchResult>(`/org/${orgId}/paytrace/transactions`, {
      params: filters,
    })
    return data
  },

  async getTransaction(orgId: string, ref: string): Promise<TransactionDetail> {
    const { data } = await apiClient.get<TransactionDetail>(
      `/org/${orgId}/paytrace/transactions/${encodeURIComponent(ref)}`,
    )
    return data
  },

  async getHealth(orgId: string, windowHours = 24): Promise<PaymentHealth> {
    const { data } = await apiClient.get<PaymentHealth>(`/org/${orgId}/paytrace/health`, {
      params: { window_hours: windowHours },
    })
    return data
  },

  async getProviders(orgId: string, windowHours = 24): Promise<ProviderStats[]> {
    const { data } = await apiClient.get<ProviderStats[]>(`/org/${orgId}/paytrace/providers`, {
      params: { window_hours: windowHours },
    })
    return data
  },

  async getAlerts(orgId: string): Promise<ProviderAlert[]> {
    const { data } = await apiClient.get<ProviderAlert[]>(`/org/${orgId}/paytrace/alerts`)
    return data
  },
}
