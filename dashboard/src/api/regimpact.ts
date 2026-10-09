import { apiClient } from './client'
import type { ImpactReport, Product, Regulation, RegulatoryRule, Workflow } from '../types/regimpact'

export interface CreateProductPayload {
  name: string
  description?: string | null
  category: string
}

export interface CreateWorkflowPayload {
  name: string
  description?: string | null
  uses_service_node_ids: string[]
  uses_product_ids: string[]
}

export interface IngestRegulationPayload {
  title: string
  source_text: string
  source_url?: string | null
  effective_date?: string | null
}

export const regimpactApi = {
  async createProduct(orgId: string, payload: CreateProductPayload): Promise<Product> {
    const { data } = await apiClient.post<Product>(`/org/${orgId}/regimpact/products`, payload)
    return data
  },

  async createWorkflow(orgId: string, payload: CreateWorkflowPayload): Promise<Workflow> {
    const { data } = await apiClient.post<Workflow>(`/org/${orgId}/regimpact/workflows`, payload)
    return data
  },

  async ingestRegulation(orgId: string, payload: IngestRegulationPayload): Promise<Regulation> {
    const { data } = await apiClient.post<Regulation>(`/org/${orgId}/regimpact/regulations`, payload)
    return data
  },

  async getRegulationRules(orgId: string, regulationId: string): Promise<RegulatoryRule[]> {
    const { data } = await apiClient.get<RegulatoryRule[]>(
      `/org/${orgId}/regimpact/regulations/${regulationId}/rules`,
    )
    return data
  },

  async getPendingRules(orgId: string): Promise<RegulatoryRule[]> {
    const { data } = await apiClient.get<RegulatoryRule[]>(`/org/${orgId}/regimpact/rules/pending`)
    return data
  },

  async getConfirmedRules(orgId: string): Promise<RegulatoryRule[]> {
    const { data } = await apiClient.get<RegulatoryRule[]>(`/org/${orgId}/regimpact/rules/confirmed`)
    return data
  },

  async reviewRule(
    orgId: string,
    ruleId: string,
    decision: 'confirmed' | 'rejected',
    note?: string,
  ): Promise<RegulatoryRule> {
    const { data } = await apiClient.post<RegulatoryRule>(`/org/${orgId}/regimpact/rules/${ruleId}/review`, {
      decision,
      note: note ?? null,
    })
    return data
  },

  async analyzeRule(orgId: string, ruleId: string): Promise<ImpactReport> {
    const { data } = await apiClient.post<ImpactReport>(`/org/${orgId}/regimpact/rules/${ruleId}/analyze`)
    return data
  },

  async listReports(orgId: string): Promise<ImpactReport[]> {
    const { data } = await apiClient.get<ImpactReport[]>(`/org/${orgId}/regimpact/reports`)
    return data
  },

  async getReport(orgId: string, reportId: string): Promise<ImpactReport> {
    const { data } = await apiClient.get<ImpactReport>(`/org/${orgId}/regimpact/reports/${reportId}`)
    return data
  },
}
