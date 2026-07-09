import { useEffect, useState } from 'react'
import { getMyMeetings, cancelMeeting } from '../api/services'
import { Card } from '../components/ui/Card'
import { Badge } from '../components/ui/Badge'
import { Button } from '../components/ui/Button'
import { Spinner } from '../components/ui/Spinner'
import { formatDate } from '../lib/utils'
import type { Meeting } from '../types'

const statusColor: Record<string, string> = {
  scheduled: 'bg-blue-100 text-blue-700',
  completed: 'bg-green-100 text-green-700',
  cancelled: 'bg-red-100 text-red-600',
  rescheduled: 'bg-yellow-100 text-yellow-700',
}

export function MeetingsPage() {
  const [meetings, setMeetings] = useState<Meeting[]>([])
  const [loading, setLoading] = useState(true)
  const [cancelling, setCancelling] = useState<number | null>(null)

  useEffect(() => {
    getMyMeetings().then(setMeetings).finally(() => setLoading(false))
  }, [])

  const handleCancel = async (id: number) => {
    if (!confirm('Cancel this meeting?')) return
    setCancelling(id)
    try {
      await cancelMeeting(id)
      setMeetings((prev) => prev.map((m) => (m.id === id ? { ...m, status: 'cancelled' } : m)))
    } finally {
      setCancelling(null)
    }
  }

  if (loading) return <div className="flex items-center justify-center h-full"><Spinner className="w-8 h-8" /></div>

  const upcoming = meetings.filter((m) => m.status === 'scheduled')
  const past = meetings.filter((m) => m.status !== 'scheduled')

  return (
    <div className="p-8 max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-900 mb-1">My Meetings</h1>
      <p className="text-gray-500 mb-6">{upcoming.length} upcoming</p>

      {meetings.length === 0 ? (
        <Card className="text-center py-16 text-gray-400">
          <p className="mb-4">No meetings scheduled yet.</p>
          <Button onClick={() => (window.location.href = '/support')}>Schedule a Meeting</Button>
        </Card>
      ) : (
        <>
          {upcoming.length > 0 && (
            <section className="mb-8">
              <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">Upcoming</h2>
              <div className="space-y-3">
                {upcoming.map((m) => (
                  <MeetingCard key={m.id} meeting={m} onCancel={handleCancel} cancelling={cancelling} />
                ))}
              </div>
            </section>
          )}
          {past.length > 0 && (
            <section>
              <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">Past</h2>
              <div className="space-y-3">
                {past.map((m) => (
                  <MeetingCard key={m.id} meeting={m} onCancel={handleCancel} cancelling={cancelling} />
                ))}
              </div>
            </section>
          )}
        </>
      )}
    </div>
  )
}

function MeetingCard({
  meeting: m,
  onCancel,
  cancelling,
}: {
  meeting: Meeting
  onCancel: (id: number) => void
  cancelling: number | null
}) {
  return (
    <div className="bg-white border border-gray-100 rounded-xl p-5">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <p className="font-semibold text-gray-900">{m.subject}</p>
            <Badge className={statusColor[m.status] ?? 'bg-gray-100 text-gray-600'}>{m.status}</Badge>
          </div>
          {m.support_user_name && (
            <p className="text-sm text-gray-500 mb-1">With {m.support_user_name}</p>
          )}
          <p className="text-sm text-gray-500">{formatDate(m.scheduled_start)} · {m.duration_minutes} min</p>
          {m.meeting_link && m.status === 'scheduled' && (
            <a
              href={m.meeting_link}
              target="_blank"
              rel="noreferrer"
              className="text-xs text-blue-600 underline mt-1 block truncate"
            >
              {m.meeting_link}
            </a>
          )}
        </div>
        {m.status === 'scheduled' && (
          <Button
            variant="outline"
            size="sm"
            onClick={() => onCancel(m.id)}
            disabled={cancelling === m.id}
          >
            {cancelling === m.id ? <Spinner className="w-3 h-3" /> : 'Cancel'}
          </Button>
        )}
      </div>
    </div>
  )
}
