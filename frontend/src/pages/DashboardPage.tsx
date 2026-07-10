import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Shield, FileText, RefreshCw, AlertTriangle, TrendingUp, MessageSquare } from 'lucide-react'
import { getMyPolicies, getMyRenewals, getNotifications } from '../api/services'
import { useAuthStore } from '../store/authStore'
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card'
import { Badge } from '../components/ui/Badge'
import { Button } from '../components/ui/Button'
import { PolicyCard } from '../components/PolicyCard'
import { formatCurrency, formatDate, daysUntil, statusColor } from '../lib/utils'
import type { Policy, Renewal, Notification } from '../types'
import { Spinner } from '../components/ui/Spinner'

export function DashboardPage() {
  const { customer, isAdmin } = useAuthStore()
  const navigate = useNavigate()
  const [policies, setPolicies] = useState<Policy[]>([])
  const [renewals, setRenewals] = useState<Renewal[]>([])
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([getMyPolicies(), getMyRenewals(), getNotifications()])
      .then(([p, r, n]) => { setPolicies(p); setRenewals(r); setNotifications(n) })
      .finally(() => setLoading(false))
  }, [])

  const activePolicies = policies.filter((p) => p.status === 'active')
  const expiringSoon = policies.filter((p) => { const d = daysUntil(p.end_date); return d >= 0 && d <= 30 })
  const pendingRenewals = renewals.filter((r) => r.status === 'pending')
  const unread = notifications.filter((n) => !n.is_read)

  if (loading) return (
    <div className="flex items-center justify-center h-full">
      <Spinner className="w-8 h-8" />
    </div>
  )

  return (
    <div className="p-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">
          Welcome back, {customer?.full_name?.split(' ')[0]} 👋
        </h1>
        <p className="text-gray-500 mt-1">Here's an overview of your insurance portfolio</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {[
          { label: 'Active Policies', value: activePolicies.length, icon: Shield, color: 'text-blue-600', bg: 'bg-blue-50' },
          { label: 'Expiring Soon', value: expiringSoon.length, icon: AlertTriangle, color: 'text-yellow-600', bg: 'bg-yellow-50' },
          { label: 'Pending Renewals', value: pendingRenewals.length, icon: RefreshCw, color: 'text-purple-600', bg: 'bg-purple-50' },
          { label: 'Unread Alerts', value: unread.length, icon: MessageSquare, color: 'text-green-600', bg: 'bg-green-50' },
        ].map(({ label, value, icon: Icon, color, bg }) => (
          <Card key={label} className="flex items-center gap-4">
            <div className={`w-12 h-12 ${bg} rounded-xl flex items-center justify-center flex-shrink-0`}>
              <Icon className={`w-6 h-6 ${color}`} />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{value}</p>
              <p className="text-sm text-gray-500">{label}</p>
            </div>
          </Card>
        ))}
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Policies */}
        <div className="lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Your Policies</h2>
            <Button variant="outline" size="sm" onClick={() => navigate('/policies')}>
              View All
            </Button>
          </div>
          {policies.length === 0 ? (
            <Card className="text-center py-12 text-gray-500">No policies found.</Card>
          ) : (
            <div className="grid sm:grid-cols-2 gap-4">
              {policies.slice(0, 4).map((p) => (
                <PolicyCard key={p.id} policy={p} onRenew={() => navigate(`/renewals?policy=${p.id}`)} />
              ))}
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Expiring Soon */}
          {expiringSoon.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-yellow-700">
                  <AlertTriangle className="w-4 h-4" /> Expiring Soon
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {expiringSoon.map((p) => (
                  <div key={p.id} className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-900">{p.policy_number}</p>
                      <p className="text-xs text-gray-500">{daysUntil(p.end_date)} days left</p>
                    </div>
                    <Button size="sm" onClick={() => navigate(`/renewals?policy=${p.id}`)}>
                      Renew
                    </Button>
                  </div>
                ))}
              </CardContent>
            </Card>
          )}

          {/* Recent Notifications */}
          <Card>
            <CardHeader>
              <CardTitle>Recent Notifications</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {notifications.slice(0, 4).map((n) => (
                <div key={n.id} className={`p-3 rounded-lg text-sm ${n.is_read ? 'bg-gray-50' : 'bg-blue-50'}`}>
                  <p className="font-medium text-gray-900 truncate">{n.subject ?? 'Notification'}</p>
                  <p className="text-gray-500 text-xs mt-0.5 line-clamp-2">{n.message}</p>
                </div>
              ))}
              {notifications.length === 0 && <p className="text-sm text-gray-500">No notifications.</p>}
              <Button variant="outline" size="sm" className="w-full" onClick={() => navigate('/notifications')}>
                View All
              </Button>
            </CardContent>
          </Card>

          {/* AI Chat CTA - customers only */}
          {!isAdmin && (
          <Card className="bg-gradient-to-br from-blue-600 to-purple-600 text-white border-0">
            <div className="flex items-center gap-3 mb-3">
              <MessageSquare className="w-6 h-6" />
              <h3 className="font-semibold">AI Assistant</h3>
            </div>
            <p className="text-sm text-blue-100 mb-4">
              Ask questions about your policies, get renewal recommendations, and more.
            </p>
            <Button
              variant="outline"
              size="sm"
              className="bg-white text-blue-600 border-white hover:bg-blue-50 w-full"
              onClick={() => navigate('/chat')}
            >
              Start Chat
            </Button>
          </Card>
          )}
        </div>
      </div>
    </div>
  )
}
