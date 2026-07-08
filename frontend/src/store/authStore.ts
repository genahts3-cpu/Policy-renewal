import { create } from 'zustand'
import type { Customer } from '../types'

interface AuthState {
  token: string | null
  customer: Customer | null
  isAdmin: boolean
  setAuth: (token: string, customer: Customer, isAdmin: boolean) => void
  logout: () => void
}

const clearChatStorage = () => {
  const uid = localStorage.getItem('customer_id') ?? 'guest'
  sessionStorage.removeItem(`chat_${uid}_messages`)
  sessionStorage.removeItem(`chat_${uid}_session_id`)
}

export const useAuthStore = create<AuthState>((set) => ({
  token: localStorage.getItem('access_token'),
  customer: null,
  isAdmin: localStorage.getItem('is_admin') === 'true',
  setAuth: (token, customer, isAdmin) => {
    clearChatStorage()
    localStorage.setItem('access_token', token)
    localStorage.setItem('is_admin', String(isAdmin))
    localStorage.setItem('customer_id', String(customer.id))
    set({ token, customer, isAdmin })
  },
  logout: () => {
    clearChatStorage()
    localStorage.clear()
    set({ token: null, customer: null, isAdmin: false })
  },
}))
