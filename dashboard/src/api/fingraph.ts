import { apiClient } from './client'
import type { CentralityScore, GraphResponse, ImpactResult, SimulationHistoryEntry } from '../types/fingraph'

export interface AddNodePayload {
  name: string
  node_type: string
  is_critical?: boolean
  alternative_for?: string | null
  metadata?: Record<string, unknown>
}

export interface AddEdgePayload {
  from_name: string
  to_name: string
  edge_type?: string
  weight?: number
}

export const fingraphApi = {
  async getGraph(orgId: string): Promise<GraphResponse> {
    const { data } = await apiClient.get<GraphResponse>(`/org/${orgId}/fingraph/graph`)
    return data
  },

  async getCriticalNodes(orgId: string): Promise<CentralityScore[]> {
    const { data } = await apiClient.get<CentralityScore[]>(`/org/${orgId}/fingraph/critical-nodes`)
    return data
  },

  async addNode(orgId: string, payload: AddNodePayload) {
    const { data } = await apiClient.post(`/org/${orgId}/fingraph/nodes`, payload)
    return data
  },

  async addEdge(orgId: string, payload: AddEdgePayload) {
    const { data } = await apiClient.post(`/org/${orgId}/fingraph/edges`, payload)
    return data
  },

  async simulate(orgId: string, nodeName: string, durationHours?: number): Promise<ImpactResult> {
    const { data } = await apiClient.post<ImpactResult>(`/org/${orgId}/fingraph/simulate`, {
      node_name: nodeName,
      duration_hours: durationHours ?? null,
    })
    return data
  },

  async simulateMulti(orgId: string, nodeNames: string[], durationHours?: number): Promise<ImpactResult> {
    const { data } = await apiClient.post<ImpactResult>(`/org/${orgId}/fingraph/simulate-multi`, {
      node_names: nodeNames,
      duration_hours: durationHours ?? null,
    })
    return data
  },

  async getHistory(orgId: string): Promise<SimulationHistoryEntry[]> {
    const { data } = await apiClient.get<SimulationHistoryEntry[]>(`/org/${orgId}/fingraph/history`)
    return data
  },
}
