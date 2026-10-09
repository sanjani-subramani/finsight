// Mirrors app/api/schemas/paytrace.py exactly.

export type TxnStage =
  | 'initiated'
  | 'gateway_accepted'
  | 'gateway_failed'
  | 'bank_accepted'
  | 'bank_failed'
  | 'webhook_sent'
  | 'webhook_failed'
  | 'settled'
  | 'settlement_failed'
  | 'refunded'

export type FailureMode =
  | 'successful'
  | 'gateway_timeout'
  | 'bank_declined'
  | 'webhook_lost'
  | 'settlement_delayed'
  | 'duplicate_attempt'
  | 'partial_failure'
  | 'stuck'
  | 'reversed'
  | 'other_failure'
  | 'in_progress'

export interface TimelineEntry {
  stage: TxnStage
  occurred_at: string
  amount: string
  provider: string
  provider_ref: string | null
  error_code: string | null
  latency_ms: number | null
}

export interface Anomaly {
  kind: string
  description: string
  from_stage: TxnStage | null
  to_stage: TxnStage | null
  occurred_at: string | null
  gap_ms: number | null
}

export interface FailureClassification {
  mode: FailureMode
  confidence: number
  evidence: Record<string, unknown>
  recommended_action: string | null
  human_summary: string
}

export interface TransactionState {
  transaction_ref: string | null
  current_stage: TxnStage | null
  timeline: TimelineEntry[]
  anomalies: Anomaly[]
  duration_by_stage: Record<string, number>
  total_duration_ms: number | null
  is_terminal: boolean
}

export interface TransactionDetail {
  state: TransactionState
  classification: FailureClassification
}

export interface TransactionSummary {
  transaction_ref: string
  current_stage: TxnStage | null
  provider: string | null
  last_event_at: string | null
  is_terminal: boolean
  failure_mode: FailureMode
  confidence: number
  recommended_action: string | null
}

export interface TransactionSearchResult {
  items: TransactionSummary[]
  total: number
  limit: number
  offset: number
}

export interface ProviderStats {
  provider: string
  total_transactions: number
  success_rate: number
  avg_latency_ms: number | null
  failure_breakdown: Record<string, number>
}

export interface PaymentHealth {
  total_transactions: number
  success_rate: number
  failure_breakdown: Record<string, number>
  avg_latency_by_stage: Record<string, number>
  p95_latency_by_stage: Record<string, number>
  webhook_success_rate: number | null
  settlement_success_rate: number
  providers: ProviderStats[]
  anomaly_count: number
  computed_at: string
}

export interface ProviderAlert {
  provider: string
  current_failure_rate: number
  baseline_failure_rate: number
  ratio: number | null
  current_transaction_count: number
  message: string
}

export interface TransactionSearchFilters {
  status?: TxnStage
  provider?: string
  date_from?: string
  date_to?: string
  failure_mode?: FailureMode
  limit?: number
  offset?: number
}
