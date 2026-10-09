import { useQuery } from '@tanstack/react-query'
import { auditApi, type AuditFilters } from '../api/audit'

export function useAuditLog(filters: AuditFilters = {}) {
  return useQuery({
    queryKey: ['audit', filters],
    queryFn: () => auditApi.listEntries(filters),
  })
}
