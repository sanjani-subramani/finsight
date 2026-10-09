// Mirrors app/api/schemas/reconx.py exactly.

export type ReconStatus =
  | 'matched'
  | 'missing_in_bank'
  | 'missing_in_gateway'
  | 'missing_in_internal'
  | 'duplicate'
  | 'amount_mismatch'
  | 'timing_difference'
  | 'unresolved'

export interface ReconciliationResult {
  result_id: string
  run_id: string
  transaction_ref: string
  status: ReconStatus
  internal_amount: string | null
  gateway_amount: string | null
  bank_amount: string | null
  probable_cause: string | null
  cause_confidence: number | null
  evidence: string[]
  resolved: boolean
  resolved_by: string | null
  resolution_note: string | null
}

export interface ReconRunSummary {
  run_id: string
  period_start: string
  period_end: string
  total_records: number
  matched: number
  missing: number
  duplicates: number
  amount_mismatches: number
  timing_differences: number
  unresolved: number
  status: string
  duration_ms: number | null
  created_at: string
}

export interface ReconRunResult {
  summary: ReconRunSummary
  results: ReconciliationResult[]
}

export interface ReconRunRequest {
  internal: Record<string, unknown>[]
  gateway: Record<string, unknown>[]
  bank: Record<string, unknown>[] | string
  amount_tolerance_pct?: number
  amount_tolerance_abs?: string
  time_window_hours?: number
  ref_similarity_threshold?: number
}
