import { apiClient } from './client'
import type { ReconRunRequest, ReconRunResult, ReconRunSummary, ReconciliationResult } from '../types/reconx'

export const reconxApi = {
  async createRun(orgId: string, payload: ReconRunRequest): Promise<ReconRunSummary> {
    const { data } = await apiClient.post<ReconRunSummary>(`/org/${orgId}/recon/runs`, payload)
    return data
  },

  async listRuns(orgId: string): Promise<ReconRunSummary[]> {
    const { data } = await apiClient.get<ReconRunSummary[]>(`/org/${orgId}/recon/runs`)
    return data
  },

  async getRun(orgId: string, runId: string): Promise<ReconRunResult> {
    const { data } = await apiClient.get<ReconRunResult>(`/org/${orgId}/recon/runs/${runId}`)
    return data
  },

  async getMismatches(orgId: string, runId: string): Promise<ReconciliationResult[]> {
    const { data } = await apiClient.get<ReconciliationResult[]>(`/org/${orgId}/recon/runs/${runId}/mismatches`)
    return data
  },

  async resolve(
    orgId: string,
    runId: string,
    resultId: string,
    resolutionNote: string,
  ): Promise<ReconciliationResult> {
    const { data } = await apiClient.post<ReconciliationResult>(
      `/org/${orgId}/recon/runs/${runId}/results/${resultId}/resolve`,
      { resolution_note: resolutionNote },
    )
    return data
  },

  exportUrl(orgId: string, runId: string): string {
    return `/org/${orgId}/recon/runs/${runId}/export?format=csv`
  },
}
