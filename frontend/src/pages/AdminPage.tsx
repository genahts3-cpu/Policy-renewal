import { useEffect, useState } from 'react'
import { Users, FileText, RefreshCw, TrendingUp, CheckCircle, Clock, AlertCircle, Upload } from 'lucide-react'
import { getAdminStats, getAdminPolicies, getAdminRenewals, getAllCustomers, uploadPdf } from '../api/services'
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card'
import { Badge } from '../components/ui/Badge'
import { Button } from '../components/ui/Button'
import { Spinner } from '../components/ui/Spinner'
import { formatCurrency, formatDate, statusColor } from '../lib/utils'
import type { AdminStats, Policy, Renewal, Customer } from '../types'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'

const COLORS = ['#2563eb', '#7c3aed', '#059669', '#d97706', '#dc2626']

export function AdminPage() {
  const [stats, setStats] = useState<AdminStats | null>(null)
  const [policies, setPolicies] = useState<Policy[]>([])
  const [renewals, setRenewals] = useState<Renewal[]>([])
  const [customers, setCustomers] = useState<Customer[]>([])
  const [tab, setTab] = useState<'overview' | 'policies' | 'renewals' | 'customers' | 'knowledge'>('overview')
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [uploadMsg, setUploadMsg] = useState('')

  useEffect(() => {
    Promise.all([getAdminStats(), getAdminPolicies(), getAdminRenewals(), getAllCustomers()])
      .then(([s, p, r, c]) => { setStats(s); setPolicies(p); setRenewals(r); setCustomers(c) })
      .finally(() => setLoading(false))
  }, [])

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    setUploading(true)
    setUploadMsg('')
    try {
      const res = await uploadPdf(file) as any
      setUploadMsg(`✅ ${res.message} (${res.chunks_added} chunks added)`)
    } catch {
      setUploadMsg('❌ Upload failed. Ensure the file is a valid PDF.')
    } finally {
      setUploading(false)
    }
  }

  if (loading) return <div className="flex items-center justify-center h-full"><Spinner className="w-8 h-8" /></div>

  const policyTypeData = ['life', 'health', 'auto', 'home', 'travel'].map((type) => ({
    name: type.charAt(0).toUpperCase() + type.slice(1),
    count: policies.filter((p) => p.policy_type === type).length,
  })).filter((d) => d.count > 0)

  const renewalStatusData = [
    { name: 'Completed', value: stats?.completed_renewals ?? 0 },
    { name: 'Pending', value: stats?.pending_renewals ?? 0 },
    { name: 'Declined', value: (stats?.total_renewals ?? 0) - (stats?.completed_renewals ?? 0) - (stats?.pending_renewals ?? 0) },
  ].filter((d) => d.value > 0)

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Admin Dashboard</h1>
        <p className="text-gray-500 mt-1">System overview and management</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-6 flex-wrap">
        {(['overview', 'policies', 'renewals', 'customers', 'knowledge'] as const).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors capitalize ${
              tab === t ? 'bg-blue-600 text-white' : 'bg-white text-gray-600 border border-gray-200 hover:bg-gray-50'
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      {tab === 'overview' && stats && (
        <>
          {/* Stats Grid */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            {[
              { label: 'Total Customers', value: stats.total_customers, icon: Users, color: 'text-blue-600', bg: 'bg-blue-50' },
              { label: 'Total Policies', value: stats.total_policies, icon: FileText, color: 'text-purple-600', bg: 'bg-purple-50' },
              { label: 'Active Policies', value: stats.active_policies, icon: CheckCircle, color: 'text-green-600', bg: 'bg-green-50' },
              { label: 'Renewal Rate', value: `${stats.renewal_rate.toFixed(1)}%`, icon: TrendingUp, color: 'text-orange-600', bg: 'bg-orange-50' },
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

          <div className="grid lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader><CardTitle>Policies by Type</CardTitle></CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={220}>
                  <BarChart data={policyTypeData}>
                    <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                    <YAxis tick={{ fontSize: 12 }} />
                    <Tooltip />
                    <Bar dataKey="count" fill="#2563eb" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader><CardTitle>Renewal Status</CardTitle></CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={220}>
                  <PieChart>
                    <Pie data={renewalStatusData} cx="50%" cy="50%" outerRadius={80} dataKey="value" label={({ name, value }) => `${name}: ${value}`}>
                      {renewalStatusData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>

          {/* Summary Cards */}
          <div className="grid grid-cols-3 gap-4 mt-6">
            {[
              { label: 'Pending Renewals', value: stats.pending_renewals, icon: Clock, color: 'text-yellow-600' },
              { label: 'Completed Renewals', value: stats.completed_renewals, icon: CheckCircle, color: 'text-green-600' },
              { label: 'Total Claims', value: stats.total_claims, icon: AlertCircle, color: 'text-red-600' },
            ].map(({ label, value, icon: Icon, color }) => (
              <Card key={label} className="text-center">
                <Icon className={`w-8 h-8 ${color} mx-auto mb-2`} />
                <p className="text-3xl font-bold text-gray-900">{value}</p>
                <p className="text-sm text-gray-500 mt-1">{label}</p>
              </Card>
            ))}
          </div>
        </>
      )}

      {tab === 'policies' && (
        <Card>
          <CardHeader><CardTitle>All Policies ({policies.length})</CardTitle></CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-100">
                    {['Policy #', 'Type', 'Customer ID', 'Premium', 'Coverage', 'Status', 'Expires'].map((h) => (
                      <th key={h} className="text-left py-3 px-2 text-gray-500 font-medium">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {policies.map((p) => (
                    <tr key={p.id} className="border-b border-gray-50 hover:bg-gray-50">
                      <td className="py-3 px-2 font-medium text-gray-900">{p.policy_number}</td>
                      <td className="py-3 px-2 capitalize">{p.policy_type}</td>
                      <td className="py-3 px-2 text-gray-500">#{p.customer_id}</td>
                      <td className="py-3 px-2">{formatCurrency(p.premium_amount)}</td>
                      <td className="py-3 px-2">{formatCurrency(p.coverage_amount)}</td>
                      <td className="py-3 px-2"><Badge className={statusColor(p.status)}>{p.status}</Badge></td>
                      <td className="py-3 px-2 text-gray-500">{formatDate(p.end_date)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}

      {tab === 'renewals' && (
        <Card>
          <CardHeader><CardTitle>All Renewals ({renewals.length})</CardTitle></CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-100">
                    {['ID', 'Policy ID', 'Customer ID', 'New Premium', 'Score', 'Status', 'Date'].map((h) => (
                      <th key={h} className="text-left py-3 px-2 text-gray-500 font-medium">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {renewals.map((r) => (
                    <tr key={r.id} className="border-b border-gray-50 hover:bg-gray-50">
                      <td className="py-3 px-2 font-medium">#{r.id}</td>
                      <td className="py-3 px-2">#{r.policy_id}</td>
                      <td className="py-3 px-2">#{r.customer_id}</td>
                      <td className="py-3 px-2">{r.new_premium ? formatCurrency(r.new_premium) : '-'}</td>
                      <td className="py-3 px-2">{r.recommendation_score ? `${(r.recommendation_score * 100).toFixed(0)}%` : '-'}</td>
                      <td className="py-3 px-2"><Badge className={statusColor(r.status)}>{r.status}</Badge></td>
                      <td className="py-3 px-2 text-gray-500">{formatDate(r.created_at)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}

      {tab === 'customers' && (
        <Card>
          <CardHeader><CardTitle>All Customers ({customers.length})</CardTitle></CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-100">
                    {['ID', 'Name', 'Email', 'Age', 'Occupation', 'Risk', 'Role', 'Joined'].map((h) => (
                      <th key={h} className="text-left py-3 px-2 text-gray-500 font-medium">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {customers.map((c) => (
                    <tr key={c.id} className="border-b border-gray-50 hover:bg-gray-50">
                      <td className="py-3 px-2 font-medium">#{c.id}</td>
                      <td className="py-3 px-2 font-medium text-gray-900">{c.full_name}</td>
                      <td className="py-3 px-2 text-gray-500">{c.email}</td>
                      <td className="py-3 px-2">{c.age ?? '-'}</td>
                      <td className="py-3 px-2">{c.occupation ?? '-'}</td>
                      <td className="py-3 px-2"><Badge className={statusColor(c.risk_profile)}>{c.risk_profile}</Badge></td>
                      <td className="py-3 px-2">{c.is_admin ? <Badge className="bg-purple-100 text-purple-800">Admin</Badge> : <Badge className="bg-gray-100 text-gray-600">Customer</Badge>}</td>
                      <td className="py-3 px-2 text-gray-500">{formatDate(c.created_at)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}

      {tab === 'knowledge' && (
        <Card className="max-w-xl">
          <CardHeader><CardTitle>Knowledge Base Management</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-gray-600">
              Upload PDF policy documents to the RAG knowledge base. The AI assistant will use these documents to answer customer questions.
            </p>
            <div className="border-2 border-dashed border-gray-200 rounded-xl p-8 text-center">
              <Upload className="w-10 h-10 text-gray-400 mx-auto mb-3" />
              <p className="text-sm font-medium text-gray-700 mb-1">Upload Policy PDF</p>
              <p className="text-xs text-gray-400 mb-4">PDF files only, max 10MB</p>
              <label className="cursor-pointer">
                <input type="file" accept=".pdf" className="hidden" onChange={handleUpload} disabled={uploading} />
                <Button variant="outline" size="sm" loading={uploading} onClick={() => {}}>
                  {uploading ? 'Uploading...' : 'Choose PDF File'}
                </Button>
              </label>
            </div>
            {uploadMsg && (
              <div className={`p-3 rounded-lg text-sm ${uploadMsg.startsWith('✅') ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'}`}>
                {uploadMsg}
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  )
}
