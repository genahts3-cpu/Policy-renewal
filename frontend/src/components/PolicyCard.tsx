import { useNavigate } from 'react-router-dom'
import { Shield, Calendar, DollarSign, ChevronRight } from 'lucide-react'
import { Card } from './ui/Card'
import { Badge } from './ui/Badge'
import { Button } from './ui/Button'
import { formatCurrency, formatDate, daysUntil, policyTypeColor, statusColor } from '../lib/utils'
import type { Policy } from '../types'

interface PolicyCardProps {
  policy: Policy
  onRenew?: (policy: Policy) => void
}

export function PolicyCard({ policy, onRenew }: PolicyCardProps) {
  const navigate = useNavigate()
  const days = daysUntil(policy.end_date)
  const isExpiringSoon = days <= 30 && days >= 0
  const isExpired = days < 0

  return (
    <Card className="hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-blue-50 rounded-lg flex items-center justify-center">
            <Shield className="w-5 h-5 text-blue-600" />
          </div>
          <div>
            <p className="font-semibold text-gray-900">{policy.policy_number}</p>
            <Badge className={policyTypeColor(policy.policy_type)}>
              {policy.policy_type.charAt(0).toUpperCase() + policy.policy_type.slice(1)}
            </Badge>
          </div>
        </div>
        <Badge className={statusColor(policy.status)}>
          {policy.status.charAt(0).toUpperCase() + policy.status.slice(1)}
        </Badge>
      </div>

      <div className="space-y-2 mb-4">
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <DollarSign className="w-4 h-4" />
          <span>Coverage: <strong>{formatCurrency(policy.coverage_amount)}</strong></span>
        </div>
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <DollarSign className="w-4 h-4" />
          <span>Premium: <strong>{formatCurrency(policy.premium_amount)}/yr</strong></span>
        </div>
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <Calendar className="w-4 h-4" />
          <span>Expires: <strong>{formatDate(policy.end_date)}</strong></span>
        </div>
      </div>

      {(isExpiringSoon || isExpired) && (
        <div className={`text-xs font-medium px-3 py-2 rounded-lg mb-3 ${isExpired ? 'bg-red-50 text-red-700' : 'bg-yellow-50 text-yellow-700'}`}>
          {isExpired ? `Expired ${Math.abs(days)} days ago` : `Expires in ${days} day${days !== 1 ? 's' : ''}`}
        </div>
      )}

      <div className="flex gap-2">
        <Button
          variant="outline"
          size="sm"
          className="flex-1"
          onClick={() => navigate(`/policies/${policy.id}`)}
        >
          View Details
        </Button>
        {(policy.status === 'active' || policy.status === 'expired') && onRenew && (
          <Button size="sm" className="flex-1" onClick={() => onRenew(policy)}>
            Renew
          </Button>
        )}
      </div>
    </Card>
  )
}
