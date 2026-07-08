import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { getMyPolicies } from '../api/services'
import { PolicyCard } from '../components/PolicyCard'
import { Spinner } from '../components/ui/Spinner'
import type { Policy } from '../types'

export function PoliciesPage() {
  const [policies, setPolicies] = useState<Policy[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('all')
  const navigate = useNavigate()

  useEffect(() => {
    getMyPolicies().then(setPolicies).finally(() => setLoading(false))
  }, [])

  const filtered = filter === 'all' ? policies : policies.filter((p) => p.status === filter)

  if (loading) return (
    <div className="flex items-center justify-center h-full">
      <Spinner className="w-8 h-8" />
    </div>
  )

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">My Policies</h1>
        <p className="text-gray-500 mt-1">{policies.length} total policies</p>
      </div>

      {/* Filter tabs */}
      <div className="flex gap-2 mb-6">
        {['all', 'active', 'expired', 'renewed'].map((s) => (
          <button
            key={s}
            onClick={() => setFilter(s)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              filter === s ? 'bg-blue-600 text-white' : 'bg-white text-gray-600 border border-gray-200 hover:bg-gray-50'
            }`}
          >
            {s.charAt(0).toUpperCase() + s.slice(1)}
          </button>
        ))}
      </div>

      {filtered.length === 0 ? (
        <div className="text-center py-16 text-gray-500">No policies found.</div>
      ) : (
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map((p) => (
            <PolicyCard
              key={p.id}
              policy={p}
              onRenew={() => navigate(`/renewals?policy=${p.id}`)}
            />
          ))}
        </div>
      )}
    </div>
  )
}
