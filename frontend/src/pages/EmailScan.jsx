import { useState } from 'react'
import api from '../api/client'
import ResultCard from '../components/ResultCard'

export default function EmailScan() {
  const [content, setContent] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const scan = async (e) => {
    e.preventDefault()
    setLoading(true); setError(''); setResult(null)
    try {
      const { data } = await api.post('/email', { content })
      setResult(data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Scan failed')
    } finally {
      setLoading(false)
    }
  }

  const examples = [
    'Hi Sarah, attached is the Q3 report for your review. Thanks, John',
    'URGENT!!! You have been SELECTED to WIN a FREE iPhone. Click NOW to claim your prize. Verify your account before it is suspended.',
    'Your package has shipped. Track it here: https://delivery-update.tk/track',
  ]

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h1 className="text-2xl font-bold">Email Spam Analyzer</h1>
        <p className="text-muted text-sm">Analyze email or SMS text for spam / phishing indicators.</p>
      </div>

      <form onSubmit={scan} className="card">
        <label className="label">Email / message content</label>
        <textarea className="input h-40 resize-none" value={content} onChange={(e) => setContent(e.target.value)} placeholder="Paste the email or SMS text here…" required />
        <div className="flex items-center justify-between mt-3">
          <div className="flex gap-2 flex-wrap">
            {examples.map((ex) => (
              <button key={ex.slice(0, 20)} type="button" onClick={() => setContent(ex)}
                className="text-xs text-muted hover:text-accent border border-line rounded-full px-3 py-1 transition">
                Sample {examples.indexOf(ex) + 1}
              </button>
            ))}
          </div>
          <button className="btn-primary" disabled={loading}>{loading ? 'Analyzing…' : 'Analyze'}</button>
        </div>
      </form>

      {error && <p className="text-danger text-sm">{error}</p>}
      {loading && <p className="text-muted text-sm animate-pulse">Running spam classifier + SHAP explanation…</p>}
      {result && <ResultCard result={result} kind="email" />}
    </div>
  )
}