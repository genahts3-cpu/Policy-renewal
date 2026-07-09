export interface Token {
  access_token: string
  token_type: string
  customer_id: number
  is_admin: boolean
  full_name: string
}

export interface Customer {
  id: number
  email: string
  full_name: string
  phone?: string
  address?: string
  date_of_birth?: string
  age?: number
  occupation?: string
  risk_profile: string
  is_active: boolean
  is_admin: boolean
  created_at: string
}

export interface Policy {
  id: number
  policy_number: string
  customer_id: number
  policy_type: string
  coverage_amount: number
  premium_amount: number
  deductible: number
  start_date: string
  end_date: string
  status: string
  description?: string
  beneficiary?: string
  created_at: string
}

export interface Renewal {
  id: number
  policy_id: number
  customer_id: number
  renewal_date?: string
  new_premium?: number
  new_end_date?: string
  status: string
  recommendation_score?: number
  recommendation_reason?: string
  ai_recommendation?: string
  created_at: string
}

export interface Claim {
  id: number
  claim_number: string
  customer_id: number
  policy_id: number
  claim_type?: string
  amount?: number
  status: string
  description?: string
  filed_date?: string
  created_at: string
}

export interface Notification {
  id: number
  customer_id: number
  channel: string
  subject?: string
  message: string
  status: string
  is_read: boolean
  policy_number?: string
  notification_type?: string
  created_at: string
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  intent?: string
  sources?: string[]
  timestamp: string
  needs_support?: boolean
  support_slots?: SlotItem[]
  support_user_id?: number
  support_user_name?: string
}

export interface SlotItem {
  start: string
  end: string
  display?: string
}

export interface Meeting {
  id: number
  customer_id: number
  support_user_id: number
  subject: string
  description?: string
  meeting_type: string
  meeting_link?: string
  google_event_id?: string
  scheduled_start: string
  scheduled_end: string
  duration_minutes: number
  status: string
  created_at: string
  updated_at: string
  support_user_name?: string
  customer_name?: string
}

export interface SupportUser {
  id: number
  name: string
  email: string
  department: string
  calendar_email?: string
  status: string
  created_at: string
}

export interface AdminStats {
  total_customers: number
  total_policies: number
  active_policies: number
  expired_policies: number
  total_renewals: number
  completed_renewals: number
  pending_renewals: number
  total_claims: number
  renewal_rate: number
}
