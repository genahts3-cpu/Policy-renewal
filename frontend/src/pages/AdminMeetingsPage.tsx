import { useEffect, useState } from 'react'
import { getAdminMeetings } from '../api/services'
import { Badge } from '../components/ui/Badge'
import { Spinner } from '../components/ui/Spinner'
import { formatDate } from '../lib/utils'
import type { Meeting } from '../types'

const statusColor: Record<string, string> = {
  scheduled: 'bg-blue-100 text-blue-700',
  completed: 'bg-green-100 text-green-700',
  cancelled: 'bg-red-100 text-red-600',
  rescheduled: 'bg-yellow-100 text-yellow-700',
}

export function AdminMeetingsPage() {
  const [meetings, setMeetings] = useState<Meeting[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('all')

  useEffect(() => {
    getAdminMeetings().then(setMeetings).finally(() => setLoading(false))
  }, [])

  const statuses = ['all', 'scheduled', 'completed', 'cancelled']
  const filtered = filter === 'all' ? meetings : meetings.filter((m) => m.status === filter)

  const counts = {
    all: meetings.length,
    scheduled: meetings.filter((m) => m.status === 'scheduled').length,
    completed: meetings.filter((m) => m.status === 'completed').length,
    cancelled: meetings.filter((m) => m.status === 'cancelled').length,
  }

  if (loading) return <div className="flex items-center justify-center h-full"><Spinner className="w-8 h-8" /></div>

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-900 mb-1">All Meetings</h1>
      <p className="text-gray-500 mb-6">{meetings.length} total meetings</p>

      {/* Filter tabs */}
      <div className="flex gap-2 mb-6">
        {statuses.map((s) => (
          <button
            key={s}
            onClick={() => setFilter(s)}
            className={`px-4 py-1.5 rounded-full text-sm font-medium transition-colors capitalize ${
              filter === s
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {s} ({counts[s as keyof typeof counts] ?? 0})
          </button>
        ))}
      </div>

      {filtered.length === 0 ? (
        <div className="text-center py-16 text-gray-400">No meetings found.</div>
      ) : (
        <div className="bg-white border border-gray-100 rounded-xl overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-100 bg-gray-50">
                <th className="text-left px-5 py-3 font-medium text-gray-500">Subject</th>
                <th className="text-left px-5 py-3 font-medium text-gray-500">Customer</th>
                <th className="text-left px-5 py-3 font-medium text-gray-500">Agent</th>
                <th className="text-left px-5 py-3 font-medium text-gray-500">Scheduled</th>
                <th className="text-left px-5 py-3 font-medium text-gray-500">Duration</th>
                <th className="text-left px-5 py-3 font-medium text-gray-500">Status</th>
                <th className="text-left px-5 py-3 font-medium text-gray-500">Link</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((m) => (
                <tr key={m.id} className="border-b border-gray-50 hover:bg-gray-50 transition-colors">
                  <td className="px-5 py-3 font-medium text-gray-900">{m.subject}</td>
                  <td className="px-5 py-3 text-gray-600">{m.customer_name ?? `#${m.customer_id}`}</td>
                  <td className="px-5 py-3 text-gray-600">{m.support_user_name ?? `#${m.support_user_id}`}</td>
                  <td className="px-5 py-3 text-gray-600">{formatDate(m.scheduled_start)}</td>
                  <td className="px-5 py-3 text-gray-600">{m.duration_minutes} min</td>
                  <td className="px-5 py-3">
                    <Badge className={statusColor[m.status] ?? 'bg-gray-100 text-gray-600'}>{m.status}</Badge>
                  </td>
                  <td className="px-5 py-3">
                    {m.meeting_link ? (
                      <a
                        href={m.meeting_link}
                        target="_blank"
                        rel="noreferrer"
                        className="text-blue-600 underline text-xs"
                      >
                        Join
                      </a>
                    ) : (
                      <span className="text-gray-300">—</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
