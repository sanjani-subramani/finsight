import { apiClient } from './client'
import type { AuditPage } from '../types/audit'

export interface AuditFilters {
  action?: string
  limit?: number
  offset?: number
}

export const auditApi = {
  async listEntries(filters: AuditFilters = {}): Promise<AuditPage> {
    const { data } = await apiClient.get<AuditPage>('/admin/audit-log', { params: filters })
    return data
  },
}
