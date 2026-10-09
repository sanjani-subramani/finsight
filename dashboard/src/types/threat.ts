export type ThreatChannel = 'sms' | 'url' | 'qr_code' | 'voice_call'
export type ThreatSeverity = 'critical' | 'high' | 'medium' | 'low' | 'none'

export interface ThreatSignal {
  name: string
  category: string
  weight: number
  evidence?: string | null
  detector?: string
  signal_type?: string
  detail?: string
  severity?: ThreatSeverity
}

export interface ThreatImpact {
  would_cause_shortfall: boolean
  prob_before: number
  prob_after: number
  obligations_at_risk: string[]
  days_until_first_impact: number | null
  human_statement: string
}

export interface ThreatEvent {
  threat_id?: string
  id?: string
  user_id?: string
  channel: ThreatChannel
  risk_score: number
  primary_category?: string
  risk_label?: string
  signals: ThreatSignal[]
  human_explanation?: string
  recommended_action?: string
  raw_input_summary?: string
  detected_at?: string
  created_at?: string
  impact?: ThreatImpact | null
}

export interface ThreatEventSummary {
  id?: string
  threat_id?: string
  channel: ThreatChannel
  risk_score: number
  primary_category?: string
  risk_label?: string
  raw_input_summary?: string
  detected_at?: string
  created_at?: string
}
