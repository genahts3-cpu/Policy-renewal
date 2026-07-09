import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { getSuggestions, bookMeeting } from '../api/services'
import { Card } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { Spinner } from '../components/ui/Spinner'
import type { SlotItem } from '../types'

export function SupportPage() {
  const navigate = useNavigate()
  const [message, setMessage] = useState('')
  const [loading, setLoading] = useState(false)
  const [slots, setSlots] = useState<SlotItem[]>([])
  const [supportUserId, setSupportUserId] = useState<number | null>(null)
  const [supportUserName, setSupportUserName] = useState('')
  const [selectedSlot, setSelectedSlot] = useState<SlotItem | null>(null)
  const [subject, setSubject] = useState('')
  const [booking, setBooking] = useState(false)
  const [booked, setBooked] = useState(false)
  const [meetingLink, setMeetingLink] = useState('')
  const [step, setStep] = useState<'input' | 'slots' | 'confirm'>('input')

  const handleRequest = async () => {
    if (!message.trim()) return
    setLoading(true)
    try {
      const res = await getSuggestions(message)
      setSlots(res.recommended_slots || [])
      setSupportUserId(res.support_user_id)
      setSupportUserName(res.support_user_name || 'Support Agent')
      setSubject(`Support Meeting - ${message.slice(0, 50)}`)
      setStep('slots')
    } finally {
      setLoading(false)
    }
  }

  const handleBook = async () => {
    if (!selectedSlot || !supportUserId) return
    setBooking(true)
    try {
      const res = await bookMeeting({ support_user_id: supportUserId, selected_slot: selectedSlot, subject })
      setMeetingLink(res.meeting_link || '')
      setBooked(true)
      setStep('confirm')
    } finally {
      setBooking(false)
    }
  }

  if (step === 'confirm') {
    return (
      <div className="p-8 max-w-xl mx-auto">
        <Card className="text-center py-12 px-8">
          <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-green-600 text-2xl">✓</span>
          </div>
          <h2 className="text-xl font-bold text-gray-900 mb-2">Meeting Booked!</h2>
          <p className="text-gray-500 mb-4">
            Your meeting with <span className="font-medium text-gray-700">{supportUserName}</span> has been scheduled.
          </p>
          {selectedSlot?.display && (
            <p className="text-sm text-blue-700 bg-blue-50 rounded-lg px-4 py-2 mb-4">{selectedSlot.display}</p>
          )}
          {meetingLink && (
            <a
              href={meetingLink}
              target="_blank"
              rel="noreferrer"
              className="block text-sm text-blue-600 underline mb-6 break-all"
            >
              {meetingLink}
            </a>
          )}
          <Button onClick={() => navigate('/meetings')}>View My Meetings</Button>
        </Card>
      </div>
    )
  }

  if (step === 'slots') {
    return (
      <div className="p-8 max-w-2xl mx-auto">
        <h1 className="text-2xl font-bold text-gray-900 mb-1">Schedule a Meeting</h1>
        <p className="text-gray-500 mb-6">
          Available slots with <span className="font-medium text-gray-700">{supportUserName}</span>
        </p>

        {slots.length === 0 ? (
          <Card className="text-center py-10 text-gray-400">No available slots found. Please try again later.</Card>
        ) : (
          <div className="grid gap-3 mb-6">
            {slots.map((slot, i) => (
              <button
                key={i}
                onClick={() => setSelectedSlot(slot)}
                className={`w-full text-left px-5 py-4 rounded-xl border transition-all ${
                  selectedSlot === slot
                    ? 'border-blue-500 bg-blue-50 text-blue-800'
                    : 'border-gray-200 bg-white text-gray-700 hover:border-blue-300'
                }`}
              >
                <p className="font-medium">{slot.display || slot.start}</p>
                {slot.display ? null : (
                  <p className="text-xs text-gray-400 mt-0.5">{slot.start} – {slot.end}</p>
                )}
              </button>
            ))}
          </div>
        )}

        <div className="flex gap-3">
          <Button variant="outline" onClick={() => setStep('input')}>Back</Button>
          <Button onClick={handleBook} disabled={!selectedSlot || booking}>
            {booking ? <Spinner className="w-4 h-4" /> : 'Confirm Booking'}
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="p-8 max-w-xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-900 mb-1">Talk to a Human</h1>
      <p className="text-gray-500 mb-6">Describe your issue and we'll connect you with a support agent.</p>

      <Card className="p-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">What do you need help with?</label>
        <textarea
          className="w-full border border-gray-200 rounded-lg px-4 py-3 text-sm text-gray-800 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
          rows={4}
          placeholder="e.g. I want to discuss my claim status or understand my policy coverage..."
          value={message}
          onChange={(e) => setMessage(e.target.value)}
        />
        <Button className="mt-4 w-full" onClick={handleRequest} disabled={!message.trim() || loading}>
          {loading ? <Spinner className="w-4 h-4" /> : 'Find Available Slots'}
        </Button>
      </Card>
    </div>
  )
}
