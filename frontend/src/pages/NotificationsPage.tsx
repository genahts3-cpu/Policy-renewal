import { useEffect, useState } from 'react'
import { Bell, CheckCheck, Mail, MessageSquare, Smartphone } from 'lucide-react'
import { getNotifications, markRead, markAllRead } from '../api/services'
import { Card } from '../components/ui/Card'
import { Badge } from '../components/ui/Badge'
import { Button } from '../components/ui/Button'
import { Spinner } from '../components/ui/Spinner'
import { formatDate } from '../lib/utils'
import type { Notification } from '../types'

const channelIcon = (channel: string) => {
  if (channel === 'email') return <Mail className="w-4 h-4" />
  if (channel === 'sms') return <Smartphone className="w-4 h-4" />
  return <Bell className="w-4 h-4" />
}

export function NotificationsPage() {
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getNotifications().then(setNotifications).finally(() => setLoading(false))
  }, [])

  const handleMarkRead = async (id: number) => {
    await markRead(id)
    setNotifications((prev) => prev.map((n) => (n.id === id ? { ...n, is_read: true } : n)))
  }

  const handleMarkAllRead = async () => {
    await markAllRead()
    setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })))
  }

  const unreadCount = notifications.filter((n) => !n.is_read).length

  if (loading) return <div className="flex items-center justify-center h-full"><Spinner className="w-8 h-8" /></div>

  return (
    <div className="p-8 max-w-3xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Notifications</h1>
          <p className="text-gray-500 mt-1">{unreadCount} unread</p>
        </div>
        {unreadCount > 0 && (
          <Button variant="outline" size="sm" onClick={handleMarkAllRead}>
            <CheckCheck className="w-4 h-4" /> Mark All Read
          </Button>
        )}
      </div>

      {notifications.length === 0 ? (
        <Card className="text-center py-16 text-gray-400">
          <Bell className="w-12 h-12 mx-auto mb-4 opacity-30" />
          <p>No notifications yet.</p>
        </Card>
      ) : (
        <div className="space-y-3">
          {notifications.map((n) => (
            <div
              key={n.id}
              className={`p-4 rounded-xl border transition-all cursor-pointer ${
                n.is_read ? 'bg-white border-gray-100' : 'bg-blue-50 border-blue-200'
              }`}
              onClick={() => !n.is_read && handleMarkRead(n.id)}
            >
              <div className="flex items-start gap-3">
                <div className={`w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0 ${
                  n.is_read ? 'bg-gray-100 text-gray-500' : 'bg-blue-100 text-blue-600'
                }`}>
                  {channelIcon(n.channel)}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    {n.subject && <p className="font-medium text-gray-900 text-sm">{n.subject}</p>}
                    {!n.is_read && <span className="w-2 h-2 bg-blue-500 rounded-full flex-shrink-0" />}
                  </div>
                  <p className="text-sm text-gray-600 leading-relaxed">{n.message}</p>
                  <div className="flex items-center gap-3 mt-2">
                    <span className="text-xs text-gray-400">{formatDate(n.created_at)}</span>
                    {n.policy_number && (
                      <Badge className="bg-gray-100 text-gray-600">{n.policy_number}</Badge>
                    )}
                    <Badge className="bg-gray-100 text-gray-500 capitalize">{n.channel}</Badge>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
