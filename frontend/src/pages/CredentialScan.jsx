import { useState } from 'react'
import api from '../api/client'
import ResultCard from '../components/ResultCard'

export default function CredentialScan() {
  const [password, setPassword] = useState('')
  const [show, setShow] = useState(false)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const scan = async (e) => {
    e.preventDefault()
    setLoading(true); setError(''); setResult(null)
    try {
      const { data } = await api.post('/credential', { password })
      setResult(data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Scan failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h1 className="text-2xl font-bold">Credential Risk Analyzer</h1>
        <p className="text-muted text-sm">Evaluate password strength using entropy, patterns and common-password checks.</p>
      </div>

      <form onSubmit={scan} className="card">
        <label className="label">Password to assess</label>
        <div className="flex gap-3">
          <input className="input font-mono" type={show ? 'text' : 'password'} value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Type a password…" required />
          <button type="button" onClick={() => setShow(!show)} className="btn-ghost shrink-0">{show ? 'Hide' : 'Show'}</button>
          <button className="btn-primary shrink-0" disabled={loading}>{loading ? 'Analyzing…' : 'Assess'}</button>
        </div>
        <p className="text-xs text-muted mt-2">Your password is analyzed in memory and never stored — only its risk profile is saved.</p>
      </form>

      {error && <p className="text-danger text-sm">{error}</p>}
      {loading && <p className="text-muted text-sm animate-pulse">Running credential risk model…</p>}
      {result && (
        <>
          <ResultCard result={result} kind="credential" />
          <div className="card">
            <div className="text-xs uppercase tracking-wider text-accent font-semibold mb-1">Shannon Entropy</div>
            <div className="text-2xl font-extrabold">{result.entropy_bits} <span className="text-sm text-muted font-normal">bits</span></div>
          </div>
        </>
      )}
    </div>
  )
}