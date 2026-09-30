import { useEffect, useState } from 'react'
import api from '../api/client'

const PRIORITY_COLOR = { high: '#ef4444', medium: '#f59e0b', low: '#22c55e' }

export default function Advisor() {
  const [tips, setTips] = useState([])
  const [loading, setLoading] = useState(true)

  const load = () => api.get('/advisor').then((r) => setTips(r.data)).finally(() => setLoading(false))
  useEffect(() => { load() }, [])

  const markAll = async () => {
    await api.post('/advisor/read-all'); load()
  }

  const markOne = async (id) => {
    await api.post(`/advisor/${id}/read`); load()
  }

  return (
    <div className="space-y-6 max-w-4xl">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">AI Security Advisor</h1>
          <p className="text-muted text-sm">Personalized tips generated from your actual scan history.</p>
        </div>
        {tips.length > 0 && (
          <button className="btn-ghost text-xs" onClick={markAll}>Mark all read</button>
        )}
      </div>

      {loading && <p className="text-muted">Loading recommendations…</p>}
      {!loading && tips.length === 0 && (
        <p className="text-muted text-sm">No tips yet. Run a few scans and your advisor will generate tailored advice.</p>
      )}

      <div className="space-y-3">
        {tips.map((t) => (
          <div key={t.id} className={`card flex gap-4 ${t.is_read ? 'opacity-60' : ''}`}>
            <div className="w-1.5 rounded-full shrink-0" style={{ background: PRIORITY_COLOR[t.priority] }} />
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-xs font-bold text-accent bg-accent/10 px-2 py-0.5 rounded">{t.category}</span>
                <span className="text-xs uppercase text-muted font-semibold">{t.priority} priority</span>
                {!t.is_read && <span className="text-xs text-ok">● new</span>}
              </div>
              <h3 className="font-semibold text-ink">{t.title}</h3>
              <p className="text-sm text-ink/80 mt-1">{t.message}</p>
              {!t.is_read && (
                <button className="text-xs text-accent mt-2" onClick={() => markOne(t.id)}>Mark as read</button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}