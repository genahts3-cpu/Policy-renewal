import { useState, useEffect, useRef } from 'react'
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import {
  uploadDocument, uploadDataset, getCollections, getDocuments,
  deleteDocument, getDatabaseStats, reimportDataset,
} from '../api/services'

const COLLECTIONS = ['insurance_policies', 'policy_faqs', 'claim_rules', 'brochures', 'terms_conditions']

interface Collection { name: string; documents: number }
interface Document { id: string; collection: string; source_file: string; chunk: number; created_at: string; preview: string }
interface DbStats {
  customers: number; policies: number; claims: number; renewals: number
  notifications: number; documents: number; embeddings: number
  collections: Collection[]
}

// ── Shared ────────────────────────────────────────────────────────────────

function StatusBadge({ status }: { status: string }) {
  const colors: Record<string, string> = {
    Indexed: 'bg-green-50 text-green-700 border border-green-200',
    imported: 'bg-green-50 text-green-700 border border-green-200',
    failed: 'bg-red-50 text-red-700 border border-red-200',
    pending: 'bg-yellow-50 text-yellow-700 border border-yellow-200',
  }
  return (
    <span className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${colors[status] ?? 'bg-gray-100 text-gray-600'}`}>
      {status}
    </span>
  )
}

function SectionTitle({ children }: { children: React.ReactNode }) {
  return <h2 className="text-base font-semibold text-[#1E3A8A] mb-4 pb-2 border-b border-gray-100">{children}</h2>
}

function StatBox({ label, value }: { label: string; value: number | string }) {
  return (
    <div className="bg-[#F8FAFC] rounded-lg p-4 border border-gray-100">
      <p className="text-2xl font-bold text-[#1E3A8A]">{value}</p>
      <p className="text-xs text-[#475569] mt-1 capitalize">{label}</p>
    </div>
  )
}

// ── Document Upload ───────────────────────────────────────────────────────

function DocumentUploadCard() {
  const [file, setFile] = useState<File | null>(null)
  const [collection, setCollection] = useState(COLLECTIONS[0])
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState('')
  const inputRef = useRef<HTMLInputElement>(null)

  const handleUpload = async () => {
    if (!file) return
    setLoading(true)
    setError('')
    setResult(null)
    try {
      const res = await uploadDocument(file, collection)
      setResult(res)
      setFile(null)
      if (inputRef.current) inputRef.current.value = ''
    } catch (e: any) {
      setError(e?.response?.data?.detail ?? 'Upload failed.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Card>
      <CardHeader><CardTitle>Document Upload</CardTitle></CardHeader>
      <CardContent className="space-y-4">
        <p className="text-xs text-[#475569]">Supported: PDF, DOCX, TXT — Max 20 MB</p>

        <div>
          <label className="block text-xs font-medium text-[#475569] mb-1">Collection</label>
          <select
            value={collection}
            onChange={(e) => setCollection(e.target.value)}
            className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {COLLECTIONS.map((c) => (
              <option key={c} value={c}>{c.replace(/_/g, ' ')}</option>
            ))}
          </select>
        </div>

        <div
          className="border-2 border-dashed border-gray-200 rounded-lg p-6 text-center cursor-pointer hover:border-blue-300 transition-colors"
          onClick={() => inputRef.current?.click()}
        >
          <p className="text-sm text-[#475569]">
            {file ? file.name : 'Click to choose a file'}
          </p>
          <input
            ref={inputRef}
            type="file"
            accept=".pdf,.docx,.txt"
            className="hidden"
            onChange={(e) => { setFile(e.target.files?.[0] ?? null); setResult(null); setError('') }}
          />
        </div>

        <Button onClick={handleUpload} disabled={!file} loading={loading} className="w-full">
          Upload and Index
        </Button>

        {error && <p className="text-xs text-[#DC2626] bg-red-50 border border-red-100 rounded p-2">{error}</p>}

        {result && (
          <div className="bg-[#F8FAFC] border border-gray-100 rounded-lg p-4 space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-[#475569]">File</span>
              <span className="font-medium text-gray-900">{result.documentName}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-[#475569]">Status</span>
              <StatusBadge status={result.status} />
            </div>
            <div className="flex justify-between">
              <span className="text-[#475569]">Collection</span>
              <span className="text-gray-700">{result.collection}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-[#475569]">Chunks Created</span>
              <span className="font-medium text-[#1E3A8A]">{result.chunks}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-[#475569]">Embeddings Generated</span>
              <span className="font-medium text-[#1E3A8A]">{result.embeddings}</span>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

// ── Dataset Upload ────────────────────────────────────────────────────────

function DatasetUploadCard({ onImported }: { onImported: () => void }) {
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState('')
  const [reimporting, setReimporting] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)
  const reimportRef = useRef<HTMLInputElement>(null)

  const handleUpload = async () => {
    if (!file) return
    setLoading(true)
    setError('')
    setResult(null)
    try {
      const res = await uploadDataset(file)
      setResult(res)
      setFile(null)
      if (inputRef.current) inputRef.current.value = ''
      onImported()
    } catch (e: any) {
      setError(e?.response?.data?.detail ?? 'Import failed.')
    } finally {
      setLoading(false)
    }
  }

  const handleReimport = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0]
    if (!f) return
    setReimporting(true)
    setError('')
    try {
      const res = await reimportDataset(f)
      setResult(res)
      onImported()
    } catch (e: any) {
      setError(e?.response?.data?.detail ?? 'Re-import failed.')
    } finally {
      setReimporting(false)
      if (reimportRef.current) reimportRef.current.value = ''
    }
  }

  return (
    <Card>
      <CardHeader><CardTitle>Dataset Upload</CardTitle></CardHeader>
      <CardContent className="space-y-4">
        <p className="text-xs text-[#475569]">Supported: CSV, XLSX — Max 20 MB</p>
        <p className="text-xs text-[#475569]">Datasets: customers, policies, claims, renewals</p>

        <div
          className="border-2 border-dashed border-gray-200 rounded-lg p-6 text-center cursor-pointer hover:border-blue-300 transition-colors"
          onClick={() => inputRef.current?.click()}
        >
          <p className="text-sm text-[#475569]">
            {file ? file.name : 'Click to choose a file'}
          </p>
          <input
            ref={inputRef}
            type="file"
            accept=".csv,.xlsx"
            className="hidden"
            onChange={(e) => { setFile(e.target.files?.[0] ?? null); setResult(null); setError('') }}
          />
        </div>

        <div className="flex gap-2">
          <Button onClick={handleUpload} disabled={!file} loading={loading} className="flex-1">
            Import Dataset
          </Button>
          <div>
            <input ref={reimportRef} type="file" accept=".csv,.xlsx" className="hidden" onChange={handleReimport} />
            <Button
              variant="outline"
              loading={reimporting}
              onClick={() => reimportRef.current?.click()}
            >
              Re-import
            </Button>
          </div>
        </div>

        {error && <p className="text-xs text-[#DC2626] bg-red-50 border border-red-100 rounded p-2">{error}</p>}

        {result && (
          <div className="bg-[#F8FAFC] border border-gray-100 rounded-lg p-4 space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-[#475569]">File</span>
              <span className="font-medium text-gray-900">{result.filename}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-[#475569]">Status</span>
              <StatusBadge status={result.status} />
            </div>
            <div className="flex justify-between">
              <span className="text-[#475569]">Dataset Type</span>
              <span className="text-gray-700 capitalize">{result.dataset_type}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-[#475569]">Records Imported</span>
              <span className="font-medium text-[#16A34A]">{result.imported}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-[#475569]">Failed Records</span>
              <span className={`font-medium ${result.failed > 0 ? 'text-[#DC2626]' : 'text-gray-500'}`}>{result.failed}</span>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

// ── Collections Table ─────────────────────────────────────────────────────

function CollectionsTable({ collections, onRefresh }: { collections: Collection[]; onRefresh: () => void }) {
  const [search, setSearch] = useState('')
  const [selectedCol, setSelectedCol] = useState<string | null>(null)
  const [docs, setDocs] = useState<Document[]>([])
  const [loadingDocs, setLoadingDocs] = useState(false)
  const [deletingId, setDeletingId] = useState<string | null>(null)

  const loadDocs = async (col?: string, q?: string) => {
    setLoadingDocs(true)
    try {
      const res = await getDocuments(q, col)
      setDocs(res)
    } catch {
      setDocs([])
    } finally {
      setLoadingDocs(false)
    }
  }

  const handleSearch = () => {
    loadDocs(selectedCol ?? undefined, search || undefined)
  }

  const handleSelectCollection = (name: string) => {
    const next = selectedCol === name ? null : name
    setSelectedCol(next)
    setSearch('')
    if (next) loadDocs(next)
    else setDocs([])
  }

  const handleDelete = async (doc: Document) => {
    setDeletingId(doc.id)
    try {
      await deleteDocument(doc.id, doc.collection)
      setDocs((prev) => prev.filter((d) => d.id !== doc.id))
      onRefresh()
    } catch {
      // silent
    } finally {
      setDeletingId(null)
    }
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Collections</CardTitle>
          <Button variant="outline" size="sm" onClick={onRefresh}>Refresh</Button>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-100">
              {['Collection', 'Documents', 'Action'].map((h) => (
                <th key={h} className="text-left py-2 px-3 text-xs font-semibold text-[#475569] uppercase tracking-wide">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {collections.map((col) => (
              <tr
                key={col.name}
                className={`border-b border-gray-50 hover:bg-[#F8FAFC] cursor-pointer ${selectedCol === col.name ? 'bg-blue-50' : ''}`}
                onClick={() => handleSelectCollection(col.name)}
              >
                <td className="py-2.5 px-3 font-medium text-gray-900">{col.name.replace(/_/g, ' ')}</td>
                <td className="py-2.5 px-3 text-[#1E3A8A] font-semibold">{col.documents}</td>
                <td className="py-2.5 px-3">
                  <button
                    className="text-xs text-[#2563EB] hover:underline"
                    onClick={(e) => { e.stopPropagation(); handleSelectCollection(col.name) }}
                  >
                    {selectedCol === col.name ? 'Hide' : 'View'}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {selectedCol && (
          <div className="mt-4 space-y-3">
            <div className="flex gap-2">
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                placeholder="Search documents..."
                className="flex-1 border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <Button size="sm" onClick={handleSearch} loading={loadingDocs}>Search</Button>
            </div>

            {loadingDocs ? (
              <p className="text-xs text-[#475569] py-4 text-center">Loading...</p>
            ) : docs.length === 0 ? (
              <p className="text-xs text-[#475569] py-4 text-center">No documents found.</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-xs">
                  <thead>
                    <tr className="border-b border-gray-100">
                      {['Source File', 'Chunk', 'Preview', 'Created', 'Delete'].map((h) => (
                        <th key={h} className="text-left py-2 px-2 text-[#475569] font-semibold uppercase tracking-wide">{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {docs.map((doc) => (
                      <tr key={doc.id} className="border-b border-gray-50 hover:bg-[#F8FAFC]">
                        <td className="py-2 px-2 font-medium text-gray-800 max-w-[120px] truncate">{doc.source_file}</td>
                        <td className="py-2 px-2 text-[#475569]">{doc.chunk}</td>
                        <td className="py-2 px-2 text-gray-600 max-w-[200px] truncate">{doc.preview}</td>
                        <td className="py-2 px-2 text-[#475569] whitespace-nowrap">{doc.created_at ? doc.created_at.slice(0, 10) : '-'}</td>
                        <td className="py-2 px-2">
                          <button
                            className="text-[#DC2626] hover:underline text-xs disabled:opacity-40"
                            disabled={deletingId === doc.id}
                            onClick={() => handleDelete(doc)}
                          >
                            {deletingId === doc.id ? '...' : 'Delete'}
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  )
}

// ── Database Statistics ───────────────────────────────────────────────────

function DatabaseStatisticsCard({ stats }: { stats: DbStats | null }) {
  if (!stats) return (
    <Card>
      <CardHeader><CardTitle>Database Statistics</CardTitle></CardHeader>
      <CardContent><p className="text-sm text-[#475569]">Loading...</p></CardContent>
    </Card>
  )

  const rows = [
    { label: 'Customers', value: stats.customers },
    { label: 'Policies', value: stats.policies },
    { label: 'Claims', value: stats.claims },
    { label: 'Renewals', value: stats.renewals },
    { label: 'Notifications', value: stats.notifications },
    { label: 'Document Chunks', value: stats.documents },
    { label: 'Embeddings', value: stats.embeddings },
  ]

  return (
    <Card>
      <CardHeader><CardTitle>Database Statistics</CardTitle></CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
          {rows.map((r) => <StatBox key={r.label} label={r.label} value={r.value} />)}
        </div>
      </CardContent>
    </Card>
  )
}

// ── Main Page ─────────────────────────────────────────────────────────────

export function DataManagementPage() {
  const [collections, setCollections] = useState<Collection[]>([])
  const [stats, setStats] = useState<DbStats | null>(null)
  const [tab, setTab] = useState<'upload' | 'collections' | 'statistics'>('upload')

  const loadCollections = async () => {
    try { setCollections(await getCollections()) } catch { /* silent */ }
  }

  const loadStats = async () => {
    try { setStats(await getDatabaseStats()) } catch { /* silent */ }
  }

  useEffect(() => {
    loadCollections()
    loadStats()
  }, [])

  const handleRefresh = () => {
    loadCollections()
    loadStats()
  }

  return (
    <div className="p-8 max-w-7xl mx-auto bg-[#F8FAFC] min-h-screen">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-[#1E3A8A]">Data Management</h1>
        <p className="text-sm text-[#475569] mt-1">Upload documents, import datasets, manage collections and monitor database statistics.</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-6">
        {([
          { key: 'upload', label: 'Upload' },
          { key: 'collections', label: 'Collections' },
          { key: 'statistics', label: 'Statistics' },
        ] as const).map(({ key, label }) => (
          <button
            key={key}
            onClick={() => setTab(key)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              tab === key
                ? 'bg-[#1E3A8A] text-white'
                : 'bg-white text-[#475569] border border-gray-200 hover:bg-gray-50'
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {tab === 'upload' && (
        <div className="grid lg:grid-cols-2 gap-6">
          <DocumentUploadCard />
          <DatasetUploadCard onImported={handleRefresh} />
        </div>
      )}

      {tab === 'collections' && (
        <CollectionsTable collections={collections} onRefresh={handleRefresh} />
      )}

      {tab === 'statistics' && (
        <div className="space-y-6">
          <DatabaseStatisticsCard stats={stats} />
          {stats?.collections && (
            <Card>
              <CardHeader><CardTitle>Collection Breakdown</CardTitle></CardHeader>
              <CardContent>
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-gray-100">
                      {['Collection', 'Document Chunks'].map((h) => (
                        <th key={h} className="text-left py-2 px-3 text-xs font-semibold text-[#475569] uppercase tracking-wide">{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {stats.collections.map((c) => (
                      <tr key={c.name} className="border-b border-gray-50 hover:bg-[#F8FAFC]">
                        <td className="py-2.5 px-3 font-medium text-gray-900">{c.name.replace(/_/g, ' ')}</td>
                        <td className="py-2.5 px-3 text-[#1E3A8A] font-semibold">{c.documents}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </CardContent>
            </Card>
          )}
        </div>
      )}
    </div>
  )
}
