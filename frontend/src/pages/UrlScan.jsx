import { useState } from 'react'
import api from '../api/client'
import ResultCard from '../components/ResultCard'

export default function UrlScan() {
  const [url, setUrl] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const scan = async (e) => {
    e.preventDefault()
    setLoading(true); setError(''); setResult(null)
    try {
      const { data } = await api.post('/url', { url })
      setResult(data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Scan failed')
    } finally {
      setLoading(false)
    }
  }

  const examples = [
    'https://github.com/anomalyco/opencode',
    'http://secure-paypal-login-verify.xyz/account/update',
    'https://www.amazon.com/deals/today?ref=nav',
  ]

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h1 className="text-2xl font-bold">URL Threat Scanner</h1>
        <p className="text-muted text-sm">Detect phishing & malicious URLs with explainable AI.</p>
      </div>

      <form onSubmit={scan} className="card">
        <label className="label">URL to analyze</label>
        <div className="flex gap-3">
          <input className="input" placeholder="https://example.com/…" value={url} onChange={(e) => setUrl(e.target.value)} required />
          <button className="btn-primary shrink-0" disabled={loading}>{loading ? 'Scanning…' : 'Analyze'}</button>
        </div>
        <div className="flex gap-2 mt-3 flex-wrap">
          {examples.map((ex) => (
            <button key={ex} type="button" onClick={() => setUrl(ex)}
              className="text-xs text-muted hover:text-accent border border-line rounded-full px-3 py-1 transition">
              {ex.slice(0, 42)}…
            </button>
          ))}
        </div>
      </form>

      {error && <p className="text-danger text-sm">{error}</p>}
      {loading && <p className="text-muted text-sm animate-pulse">Running ML model + SHAP explanation…</p>}
      {result && <ResultCard result={result} kind="url" />}
    </div>
  )
}