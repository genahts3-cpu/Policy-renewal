import api from './client'
import type { Token, Customer, Policy, Renewal, Notification, AdminStats, Claim } from '../types'

// Auth
export const login = (email: string, password: string) =>
  api.post<Token>('/auth/login', { email, password }).then((r) => r.data)

export const register = (data: Partial<Customer> & { password: string }) =>
  api.post<Customer>('/auth/register', data).then((r) => r.data)

// Customers
export const getMe = (token?: string) =>
  api.get<Customer>('/customers/me', token ? { headers: { Authorization: `Bearer ${token}` } } : undefined).then((r) => r.data)
export const updateMe = (data: Partial<Customer>) =>
  api.put<Customer>('/customers/me', data).then((r) => r.data)
export const getAllCustomers = () => api.get<Customer[]>('/customers/').then((r) => r.data)

// Policies
export const getMyPolicies = () => api.get<Policy[]>('/policies/').then((r) => r.data)
export const getPolicy = (id: number) => api.get<Policy>(`/policies/${id}`).then((r) => r.data)
export const getPolicyClaims = (id: number) =>
  api.get<Claim[]>(`/policies/${id}/claims`).then((r) => r.data)

// Renewals
export const getMyRenewals = () => api.get<Renewal[]>('/renewals/').then((r) => r.data)
export const getRenewalRecommendation = (policyId: number) =>
  api.post<Renewal>(`/renewals/recommend/${policyId}`).then((r) => r.data)
export const confirmRenewal = (renewalId: number) =>
  api.post<Renewal>(`/renewals/${renewalId}/confirm`).then((r) => r.data)
export const declineRenewal = (renewalId: number) =>
  api.post<Renewal>(`/renewals/${renewalId}/decline`).then((r) => r.data)

// Chat
export const sendChat = (message: string, sessionId?: string) =>
  api
    .post<{ response: string; intent: string; session_id: string; sources: string[] }>('/chat/', {
      message,
      session_id: sessionId,
    })
    .then((r) => r.data)

// Notifications
export const getNotifications = () =>
  api.get<Notification[]>('/notifications/').then((r) => r.data)
export const getUnreadCount = () =>
  api.get<{ count: number }>('/notifications/unread-count').then((r) => r.data)
export const markRead = (id: number) =>
  api.put(`/notifications/${id}/read`).then((r) => r.data)
export const markAllRead = () => api.put('/notifications/read-all').then((r) => r.data)

// Admin
export const getAdminStats = () => api.get<AdminStats>('/admin/stats').then((r) => r.data)
export const getAdminPolicies = () => api.get<Policy[]>('/admin/policies').then((r) => r.data)
export const getAdminRenewals = () => api.get<Renewal[]>('/admin/renewals').then((r) => r.data)

// Knowledge
export const uploadPdf = (file: File) => {
  const form = new FormData()
  form.append('file', file)
  return api.post('/knowledge/upload-pdf', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }).then((r) => r.data)
}
