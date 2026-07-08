import { create } from 'zustand'
import type { Customer } from '../types'

interface AuthState {
  token: string | null
  customer: Customer | null
  isAdmin: boolean
  setAuth: (token: string, customer: Customer, isAdmin: boolean) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  token: localStorage.getItem('access_token'),
  customer: null,
  isAdmin: localStorage.getItem('is_admin') === 'true',
  setAuth: (token, customer, isAdmin) => {
    localStorage.setItem('access_token', token)
    localStorage.setItem('is_admin', String(isAdmin))
    set({ token, customer, isAdmin })
  },
  logout: () => {
    localStorage.clear()
    set({ token: null, customer: null, isAdmin: false })
  },
}))
