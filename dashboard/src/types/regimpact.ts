// Mirrors app/api/schemas/regimpact.py exactly.

export type RuleStatus = 'pending_review' | 'confirmed' | 'rejected'

export interface Product {
  id: string
  name: string
  description: string | null
  category: string
}

export interface Workflow {
  id: string
  name: string
  description: string | null
  uses_service_node_ids: string[]
  uses_product_ids: string[]
}

export interface Regulation {
  id: string
  title: string
  source_url: string | null
  effective_date: string | null
  ingested_at: string
}

export interface RegulatoryRule {
  id: string
  regulation_id: string
  rule_text: string
  trigger_condition: string
  threshold_json: Record<string, unknown> | null
  required_action: string
  deadline_days: number | null
  applies_to_product_categories: string[]
  extraction_confidence: number | null
  ambiguities: string[]
  status: RuleStatus
  reviewed_by: string | null
  reviewed_at: string | null
  review_note: string | null
}

export interface ImpactReport {
  id: string
  regulation_id: string
  rule_id: string
  affected_products: string[]
  affected_workflows: string[]
  affected_service_nodes: string[]
  estimated_transactions: number
  required_changes: string[]
  generated_at: string
}
