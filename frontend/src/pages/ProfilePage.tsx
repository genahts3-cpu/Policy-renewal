import { useEffect, useState } from 'react'
import { User, Mail, Phone, MapPin, Briefcase, Calendar, Shield } from 'lucide-react'
import { getMe, updateMe } from '../api/services'
import { useAuthStore } from '../store/authStore'
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card'
import { Badge } from '../components/ui/Badge'
import { Button } from '../components/ui/Button'
import { Spinner } from '../components/ui/Spinner'
import type { Customer } from '../types'

export function ProfilePage() {
  const { setAuth, token, isAdmin } = useAuthStore()
  const [customer, setCustomer] = useState<Customer | null>(null)
  const [editing, setEditing] = useState(false)
  const [form, setForm] = useState({ full_name: '', phone: '', address: '', occupation: '' })
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    getMe().then((c) => {
      setCustomer(c)
      setForm({ full_name: c.full_name, phone: c.phone ?? '', address: c.address ?? '', occupation: c.occupation ?? '' })
    }).finally(() => setLoading(false))
  }, [])

  const handleSave = async () => {
    setSaving(true)
    try {
      const updated = await updateMe(form)
      setCustomer(updated)
      setAuth(token!, updated, isAdmin)
      setEditing(false)
      setSaved(true)
      setTimeout(() => setSaved(false), 3000)
    } finally {
      setSaving(false)
    }
  }

  if (loading) return <div className="flex items-center justify-center h-full"><Spinner className="w-8 h-8" /></div>
  if (!customer) return null

  const riskColor = { low: 'bg-green-100 text-green-800', medium: 'bg-yellow-100 text-yellow-800', high: 'bg-red-100 text-red-800' }

  return (
    <div className="p-8 max-w-3xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">My Profile</h1>
        <p className="text-gray-500 mt-1">Manage your account information</p>
      </div>

      {saved && (
        <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg text-sm mb-4">
          Profile updated successfully!
        </div>
      )}

      {/* Avatar + Summary */}
      <Card className="mb-6">
        <div className="flex items-center gap-5">
          <div className="w-16 h-16 bg-blue-100 rounded-2xl flex items-center justify-center">
            <span className="text-blue-700 font-bold text-2xl">{customer.full_name[0]}</span>
          </div>
          <div className="flex-1">
            <h2 className="text-xl font-bold text-gray-900">{customer.full_name}</h2>
            <p className="text-gray-500 text-sm">{customer.email}</p>
            <div className="flex items-center gap-2 mt-2">
              <Badge className={riskColor[customer.risk_profile as keyof typeof riskColor] ?? 'bg-gray-100 text-gray-800'}>
                {customer.risk_profile} risk
              </Badge>
              {customer.is_admin && <Badge className="bg-purple-100 text-purple-800">Admin</Badge>}
            </div>
          </div>
          <Button variant="outline" size="sm" onClick={() => setEditing(!editing)}>
            {editing ? 'Cancel' : 'Edit Profile'}
          </Button>
        </div>
      </Card>

      {editing ? (
        <Card>
          <CardHeader><CardTitle>Edit Information</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            {[
              { label: 'Full Name', key: 'full_name', type: 'text' },
              { label: 'Phone', key: 'phone', type: 'tel' },
              { label: 'Address', key: 'address', type: 'text' },
              { label: 'Occupation', key: 'occupation', type: 'text' },
            ].map(({ label, key, type }) => (
              <div key={key}>
                <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
                <input
                  type={type}
                  value={form[key as keyof typeof form]}
                  onChange={(e) => setForm((f) => ({ ...f, [key]: e.target.value }))}
                  className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            ))}
            <Button loading={saving} onClick={handleSave}>Save Changes</Button>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardHeader><CardTitle>Account Information</CardTitle></CardHeader>
          <CardContent>
            <div className="space-y-4">
              {[
                { icon: User, label: 'Full Name', value: customer.full_name },
                { icon: Mail, label: 'Email', value: customer.email },
                { icon: Phone, label: 'Phone', value: customer.phone ?? 'Not provided' },
                { icon: MapPin, label: 'Address', value: customer.address ?? 'Not provided' },
                { icon: Briefcase, label: 'Occupation', value: customer.occupation ?? 'Not provided' },
                { icon: Calendar, label: 'Date of Birth', value: customer.date_of_birth ?? 'Not provided' },
                { icon: Calendar, label: 'Age', value: customer.age ? `${customer.age} years` : 'Not provided' },
                { icon: Shield, label: 'Member Since', value: new Date(customer.created_at).toLocaleDateString() },
              ].map(({ icon: Icon, label, value }) => (
                <div key={label} className="flex items-center gap-3 py-2 border-b border-gray-50 last:border-0">
                  <Icon className="w-4 h-4 text-gray-400 flex-shrink-0" />
                  <span className="text-sm text-gray-500 w-32 flex-shrink-0">{label}</span>
                  <span className="text-sm font-medium text-gray-900">{value}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
