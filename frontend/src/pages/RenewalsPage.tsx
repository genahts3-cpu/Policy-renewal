import { useEffect, useState } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import { RefreshCw, CheckCircle, XCircle, TrendingUp, Star } from 'lucide-react'
import { getMyPolicies, getMyRenewals, getRenewalRecommendation, confirmRenewal, declineRenewal } from '../api/services'
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card'
import { Badge } from '../components/ui/Badge'
import { Button } from '../components/ui/Button'
import { Spinner } from '../components/ui/Spinner'
import { formatCurrency, formatDate, statusColor } from '../lib/utils'
import type { Policy, Renewal } from '../types'

export function RenewalsPage() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const [policies, setPolicies] = useState<Policy[]>([])
  const [renewals, setRenewals] = useState<Renewal[]>([])
  const [selectedPolicy, setSelectedPolicy] = useState<Policy | null>(null)
  const [currentRenewal, setCurrentRenewal] = useState<Renewal | null>(null)
  const [loading, setLoading] = useState(true)
  const [recommending, setRecommending] = useState(false)
  const [confirming, setConfirming] = useState(false)

  useEffect(() => {
    Promise.all([getMyPolicies(), getMyRenewals()])
      .then(([p, r]) => {
        setPolicies(p)
        setRenewals(r)
        const policyId = searchParams.get('policy')
        if (policyId) {
          const found = p.find((pol) => pol.id === parseInt(policyId))
          if (found) setSelectedPolicy(found)
        }
      })
      .finally(() => setLoading(false))
  }, [])

  const handleGetRecommendation = async (policy: Policy) => {
    setSelectedPolicy(policy)
    setCurrentRenewal(null)
    setRecommending(true)
    try {
      const renewal = await getRenewalRecommendation(policy.id)
      setCurrentRenewal(renewal)
    } finally {
      setRecommending(false)
    }
  }

  const handleConfirm = async () => {
    if (!currentRenewal) return
    setConfirming(true)
    try {
      const updated = await confirmRenewal(currentRenewal.id)
      setCurrentRenewal(updated)
      setRenewals((prev) => prev.map((r) => (r.id === updated.id ? updated : r)))
    } finally {
      setConfirming(false)
    }
  }

  const handleDecline = async () => {
    if (!currentRenewal) return
    const updated = await declineRenewal(currentRenewal.id)
    setCurrentRenewal(updated)
    setRenewals((prev) => prev.map((r) => (r.id === updated.id ? updated : r)))
  }

  if (loading) return <div className="flex items-center justify-center h-full"><Spinner className="w-8 h-8" /></div>

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Policy Renewals</h1>
        <p className="text-gray-500 mt-1">AI-powered renewal recommendations</p>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Policy Selection */}
        <div>
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Select a Policy to Renew</h2>
          <div className="space-y-3">
            {policies.filter((p) => ['active', 'expired'].includes(p.status)).map((p) => (
              <div
                key={p.id}
                className={`p-4 rounded-xl border-2 cursor-pointer transition-all ${
                  selectedPolicy?.id === p.id ? 'border-blue-500 bg-blue-50' : 'border-gray-100 bg-white hover:border-gray-300'
                }`}
                onClick={() => setSelectedPolicy(p)}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-semibold text-gray-900">{p.policy_number}</p>
                    <p className="text-sm text-gray-500 capitalize">{p.policy_type} Insurance</p>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold text-gray-900">{formatCurrency(p.premium_amount)}/yr</p>
                    <Badge className={statusColor(p.status)}>{p.status}</Badge>
                  </div>
                </div>
                {selectedPolicy?.id === p.id && (
                  <Button
                    className="mt-3 w-full"
                    loading={recommending}
                    onClick={(e) => { e.stopPropagation(); handleGetRecommendation(p) }}
                  >
                    <TrendingUp className="w-4 h-4" />
                    Get AI Recommendation
                  </Button>
                )}
              </div>
            ))}
          </div>

          {/* Past Renewals */}
          {renewals.length > 0 && (
            <div className="mt-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Renewal History</h2>
              <div className="space-y-2">
                {renewals.map((r) => (
                  <div key={r.id} className="flex items-center justify-between p-3 bg-white rounded-lg border border-gray-100">
                    <div>
                      <p className="text-sm font-medium text-gray-900">Renewal #{r.id}</p>
                      <p className="text-xs text-gray-500">{formatDate(r.created_at)}</p>
                    </div>
                    <div className="text-right">
                      {r.new_premium && <p className="text-sm font-semibold">{formatCurrency(r.new_premium)}/yr</p>}
                      <Badge className={statusColor(r.status)}>{r.status}</Badge>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Recommendation Panel */}
        <div>
          {recommending && (
            <Card className="text-center py-16">
              <Spinner className="w-10 h-10 mx-auto mb-4" />
              <p className="text-gray-600 font-medium">AI is analyzing your policy...</p>
              <p className="text-gray-400 text-sm mt-1">Generating personalized recommendation</p>
            </Card>
          )}

          {!recommending && currentRenewal && (
            <Card>
              <CardHeader>
                <div className="flex items-center gap-2">
                  <Star className="w-5 h-5 text-yellow-500" />
                  <CardTitle>AI Recommendation</CardTitle>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Score */}
                <div className="bg-blue-50 rounded-xl p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-blue-700">Renewal Probability</span>
                    <span className="text-2xl font-bold text-blue-700">
                      {((currentRenewal.recommendation_score ?? 0) * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div className="w-full bg-blue-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all"
                      style={{ width: `${(currentRenewal.recommendation_score ?? 0) * 100}%` }}
                    />
                  </div>
                </div>

                {/* New Premium */}
                {currentRenewal.new_premium && (
                  <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                    <span className="text-sm text-green-700 font-medium">Recommended Premium</span>
                    <span className="text-lg font-bold text-green-700">{formatCurrency(currentRenewal.new_premium)}/yr</span>
                  </div>
                )}

                {/* AI Message */}
                {currentRenewal.ai_recommendation && (
                  <div className="p-4 bg-gray-50 rounded-xl">
                    <p className="text-sm text-gray-700 leading-relaxed">{currentRenewal.ai_recommendation}</p>
                  </div>
                )}

                {/* Reasons */}
                {currentRenewal.recommendation_reason && (
                  <div>
                    <p className="text-sm font-medium text-gray-700 mb-2">Key Reasons:</p>
                    <ul className="space-y-1">
                      {currentRenewal.recommendation_reason.split(', ').map((r, i) => (
                        <li key={i} className="flex items-start gap-2 text-sm text-gray-600">
                          <CheckCircle className="w-4 h-4 text-green-500 flex-shrink-0 mt-0.5" />
                          {r}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* New End Date */}
                {currentRenewal.new_end_date && (
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-500">New Expiry Date</span>
                    <span className="font-medium text-gray-900">{formatDate(currentRenewal.new_end_date)}</span>
                  </div>
                )}

                {/* Actions */}
                {currentRenewal.status === 'pending' && (
                  <div className="flex gap-3 pt-2">
                    <Button className="flex-1" loading={confirming} onClick={handleConfirm}>
                      <CheckCircle className="w-4 h-4" /> Confirm Renewal
                    </Button>
                    <Button variant="outline" className="flex-1" onClick={handleDecline}>
                      <XCircle className="w-4 h-4" /> Decline
                    </Button>
                  </div>
                )}

                {currentRenewal.status === 'completed' && (
                  <div className="flex items-center gap-2 p-3 bg-green-50 rounded-lg text-green-700">
                    <CheckCircle className="w-5 h-5" />
                    <span className="font-medium">Policy successfully renewed!</span>
                  </div>
                )}

                {currentRenewal.status === 'declined' && (
                  <div className="flex items-center gap-2 p-3 bg-red-50 rounded-lg text-red-700">
                    <XCircle className="w-5 h-5" />
                    <span className="font-medium">Renewal declined.</span>
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {!recommending && !currentRenewal && (
            <Card className="text-center py-16 text-gray-400">
              <RefreshCw className="w-12 h-12 mx-auto mb-4 opacity-30" />
              <p className="font-medium">Select a policy and click</p>
              <p className="text-sm">"Get AI Recommendation" to start</p>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}
