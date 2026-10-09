import { apiClient } from './client'
import type { OrgMembershipResponse, TokenResponse, UserResponse } from '../types/auth'

export const authApi = {
  async register(payload: { email: string; password: string; display_name?: string }): Promise<UserResponse> {
    const { data } = await apiClient.post<UserResponse>('/auth/register', payload)
    return data
  },

  async login(email: string, password: string): Promise<TokenResponse> {
    const { data } = await apiClient.post<TokenResponse>('/auth/login', { email, password })
    return data
  },

  async logout(refreshToken: string): Promise<void> {
    await apiClient.post('/auth/logout', { refresh_token: refreshToken })
  },

  async me(): Promise<UserResponse> {
    const { data } = await apiClient.get<UserResponse>('/auth/me')
    return data
  },

  async myOrgs(): Promise<OrgMembershipResponse[]> {
    const { data } = await apiClient.get<OrgMembershipResponse[]>('/auth/my-orgs')
    return data
  },
}
