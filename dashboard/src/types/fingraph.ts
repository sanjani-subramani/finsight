// Mirrors app/api/schemas/fingraph.py exactly.

export interface DependencyNode {
  id: string
  name: string
  node_type: string
  is_critical: boolean
  alternative_for: string | null
  metadata: Record<string, unknown>
}

export interface DependencyEdge {
  from_name: string
  to_name: string
  edge_type: string
  weight: number
}

export interface GraphResponse {
  nodes: DependencyNode[]
  edges: DependencyEdge[]
  cycle_warnings: string[]
}

export interface CentralityScore {
  node_name: string
  betweenness: number
  is_critical: boolean
  node_type: string
}

export interface ImpactResult {
  impact_id: string
  failed_node: string
  affected_services: string[]
  affected_workflows: string[]
  estimated_transactions: number
  critical_paths: string[][]
  alternative_providers: string[]
}

export interface SimulationHistoryEntry {
  id: string
  failed_node: string
  duration_hours: number | null
  result: ImpactResult
  created_at: string
}
