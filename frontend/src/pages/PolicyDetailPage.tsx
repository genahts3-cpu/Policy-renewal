import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Shield, Calendar, DollarSign, User, FileText } from 'lucide-react'
import { getPolicy, getPolicyClaims } from '../api/services'
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card'
import { Badge } from '../components/ui/Badge'
import { Button } from '../components/ui/Button'
import { Spinner } from '../components/ui/Spinner'
import { formatCurrency, formatDate, daysUntil, policyTypeColor, statusColor } from '../lib/utils'
import type { Policy, Claim } from '../types'

export function PolicyDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [policy, setPolicy] = useState<Policy | null>(null)
  const [claims, setClaims] = useState<Claim[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!id) return
    Promise.all([getPolicy(parseInt(id)), getPolicyClaims(parseInt(id))])
      .then(([p, c]) => { setPolicy(p); setClaims(c) })
      .finally(() => setLoading(false))
  }, [id])

  if (loading) return <div className="flex items-center justify-center h-full"><Spinner className="w-8 h-8" /></div>
  if (!policy) return <div className="p-8 text-gray-500">Policy not found.</div>

  const days = daysUntil(policy.end_date)

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <button onClick={() => navigate(-1)} className="flex items-center gap-2 text-gray-500 hover:text-gray-900 mb-6 text-sm">
        <ArrowLeft className="w-4 h-4" /> Back
      </button>

      <div className="flex items-start justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{policy.policy_number}</h1>
          <div className="flex items-center gap-2 mt-2">
            <Badge className={policyTypeColor(policy.policy_type)}>
              {policy.policy_type.charAt(0).toUpperCase() + policy.policy_type.slice(1)} Insurance
            </Badge>
            <Badge className={statusColor(policy.status)}>
              {policy.status.charAt(0).toUpperCase() + policy.status.slice(1)}
            </Badge>
          </div>
        </div>
        {(policy.status === 'active' || policy.status === 'expired') && (
          <Button onClick={() => navigate(`/renewals?policy=${policy.id}`)}>
            Renew Policy
          </Button>
        )}
      </div>

      <div className="grid md:grid-cols-2 gap-6 mb-6">
        <Card>
          <CardHeader><CardTitle>Coverage Details</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            {[
              { icon: DollarSign, label: 'Coverage Amount', value: formatCurrency(policy.coverage_amount) },
              { icon: DollarSign, label: 'Annual Premium', value: formatCurrency(policy.premium_amount) },
              { icon: DollarSign, label: 'Deductible', value: formatCurrency(policy.deductible) },
              { icon: User, label: 'Beneficiary', value: policy.beneficiary ?? 'N/A' },
            ].map(({ icon: Icon, label, value }) => (
              <div key={label} className="flex items-center justify-between py-2 border-b border-gray-50 last:border-0">
                <div className="flex items-center gap-2 text-gray-500 text-sm">
                  <Icon className="w-4 h-4" /> {label}
                </div>
                <span className="font-semibold text-gray-900 text-sm">{value}</span>
              </div>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Policy Period</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            {[
              { label: 'Start Date', value: formatDate(policy.start_date) },
              { label: 'End Date', value: formatDate(policy.end_date) },
              { label: 'Days Remaining', value: days >= 0 ? `${days} days` : `Expired ${Math.abs(days)} days ago` },
            ].map(({ label, value }) => (
              <div key={label} className="flex items-center justify-between py-2 border-b border-gray-50 last:border-0">
                <span className="text-gray-500 text-sm">{label}</span>
                <span className={`font-semibold text-sm ${days < 0 ? 'text-red-600' : days <= 30 ? 'text-yellow-600' : 'text-gray-900'}`}>{value}</span>
              </div>
            ))}
            {days >= 0 && days <= 30 && (
              <div className="bg-yellow-50 text-yellow-700 text-xs px-3 py-2 rounded-lg mt-2">
                ⚠️ This policy expires soon. Consider renewing now.
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {policy.description && (
        <Card className="mb-6">
          <CardHeader><CardTitle>Description</CardTitle></CardHeader>
          <CardContent>
            <p className="text-gray-600 text-sm">{policy.description}</p>
          </CardContent>
        </Card>
      )}

      {/* Claims */}
      <Card>
        <CardHeader>
          <CardTitle>Claims History ({claims.length})</CardTitle>
        </CardHeader>
        <CardContent>
          {claims.length === 0 ? (
            <p className="text-gray-500 text-sm">No claims filed for this policy.</p>
          ) : (
            <div className="space-y-3">
              {claims.map((c) => (
                <div key={c.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p className="text-sm font-medium text-gray-900">{c.claim_number}</p>
                    <p className="text-xs text-gray-500">{c.claim_type} • {c.filed_date}</p>
                    <p className="text-xs text-gray-500 mt-0.5">{c.description}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-semibold text-gray-900">{formatCurrency(c.amount ?? 0)}</p>
                    <Badge className={statusColor(c.status)}>{c.status}</Badge>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
