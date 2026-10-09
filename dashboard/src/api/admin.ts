import { apiClient } from './client'
import type { QueueDepthResponse, DlqMessageResponse, DlqReplayResponse, WorkerHealthResponse } from '../types/admin'

export const adminApi = {
  async getQueues(): Promise<QueueDepthResponse[]> {
    const { data } = await apiClient.get<QueueDepthResponse[]>('/admin/queues')
    return data
  },

  async getDlq(limit = 50): Promise<DlqMessageResponse[]> {
    const { data } = await apiClient.get<DlqMessageResponse[]>('/admin/dlq', { params: { limit } })
    return data
  },

  async replayDlq(messageId: string): Promise<DlqReplayResponse> {
    const { data } = await apiClient.post<DlqReplayResponse>(`/admin/dlq/${messageId}/replay`)
    return data
  },

  async deleteDlq(messageId: string): Promise<void> {
    await apiClient.delete(`/admin/dlq/${messageId}`)
  },

  async getWorkerHealth(): Promise<WorkerHealthResponse> {
    const { data } = await apiClient.get<WorkerHealthResponse>('/admin/worker-health')
    return data
  },
}

export const reportsApi = {
  async getPipelineMetrics(): Promise<any> {
    const { data } = await apiClient.get('/reports/pipeline-metrics')
    return data
  },
  
  async getShadowReport(): Promise<any> {
    const { data } = await apiClient.get('/reports/shadow-precision')
    return data
  },

  async getLoadTestReport(): Promise<any> {
    const { data } = await apiClient.get('/reports/load-test')
    return data
  }
}
