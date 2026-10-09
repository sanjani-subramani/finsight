import { apiClient } from './client'
import type { ThreatEvent, ThreatEventSummary } from '../types/threat'

export const threatApi = {
  async listThreats(): Promise<ThreatEventSummary[]> {
    const { data } = await apiClient.get<ThreatEventSummary[]>('/threat/events')
    return data
  },

  async getThreat(threatId: string): Promise<ThreatEvent> {
    const { data } = await apiClient.get<ThreatEvent>(`/threat/events/${threatId}`)
    return data
  },

  async analyzeSms(body: string): Promise<ThreatEvent> {
    const { data } = await apiClient.post<ThreatEvent>('/threat/sms', { body })
    return data
  },

  async analyzeUrl(url: string): Promise<ThreatEvent> {
    const { data } = await apiClient.post<ThreatEvent>('/threat/url', { url })
    return data
  },

  async analyzeQr(imageFile: File): Promise<ThreatEvent> {
    const formData = new FormData()
    formData.append('image', imageFile)
    const { data } = await apiClient.post<ThreatEvent>('/threat/qr', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return data
  },

  async analyzeCall(audioFile: File): Promise<ThreatEvent> {
    const formData = new FormData()
    formData.append('audio', audioFile)
    const { data } = await apiClient.post<ThreatEvent>('/threat/call', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return data
  },
}
