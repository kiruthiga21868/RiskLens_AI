import { useEffect, useState } from 'react'
import api from '../api/client'
import { RiskBadge } from '../components/ui'

export default function Threats() {
  const [items, setItems] = useState([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    api.get('/threats', { params: { page, page_size: 15 } })
      .then((r) => { setItems(r.data.items); setTotal(r.data.total) })
      .finally(() => setLoading(false))
  }, [page])

  const pages = Math.max(1, Math.ceil(total / 15))

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Threat History</h1>
        <p className="text-muted text-sm">{total} assessments recorded.</p>
      </div>

      {loading && <p className="text-muted">Loading…</p>}
      <div className="space-y-3">
        {items.map((a) => (
          <div key={a.id} className="card">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <span className="uppercase text-xs font-bold text-accent bg-accent/10 px-2 py-0.5 rounded">{a.type}</span>
                <span className="text-sm font-semibold capitalize text-ink">{a.prediction}</span>
              </div>
              <div className="flex items-center gap-3">
                <RiskBadge score={a.risk_score} />
                <span className="text-xs text-muted">{a.created_at ? new Date(a.created_at).toLocaleString() : ''}</span>
              </div>
            </div>
            <p className="text-sm text-ink/80 line-clamp-2">{a.content}</p>
          </div>
        ))}
      </div>

      {items.length === 0 && !loading && <p className="text-muted text-sm">No threats yet.</p>}

      <div className="flex items-center justify-center gap-3 pt-2">
        <button className="btn-ghost text-sm disabled:opacity-40" disabled={page <= 1} onClick={() => setPage(page - 1)}>Prev</button>
        <span className="text-sm text-muted">Page {page} of {pages}</span>
        <button className="btn-ghost text-sm disabled:opacity-40" disabled={page >= pages} onClick={() => setPage(page + 1)}>Next</button>
      </div>
    </div>
  )
}