export interface AuditEntry {
  id: string
  actor_user_id: string | null
  actor_email: string | null
  action: string
  resource_type: string
  resource_id: string | null
  ip_address: string | null
  trace_id: string | null
  created_at: string
  detail: string | null
}

export interface AuditPage {
  items: AuditEntry[]
  total: number
}
