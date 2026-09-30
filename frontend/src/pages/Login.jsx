import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ username: '', password: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const submit = async (e) => {
    e.preventDefault()
    setLoading(true); setError('')
    try {
      const user = await login(form.username, form.password)
      navigate(user.role === 'admin' ? '/admin' : '/')
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen grid lg:grid-cols-2">
      <div className="hidden lg:flex flex-col justify-between p-12 bg-gradient-to-br from-panel via-panel2 to-base border-r border-line">
        <div className="flex items-center gap-2">
          <div className="w-9 h-9 rounded-lg bg-accent/20 border border-accent/40 grid place-items-center">
            <span className="text-accent font-extrabold">R</span>
          </div>
          <span className="font-bold text-lg">RiskLens AI</span>
        </div>
        <div>
          <h1 className="text-4xl font-extrabold leading-tight mb-4">
            Know Your Digital Risk<br />Before It Becomes a Threat.
          </h1>
          <p className="text-muted mb-6 max-w-md">
            AI-powered URL, email and credential threat detection with explainable
            predictions, a dynamic Cyber Health Score and personalized security advice.
          </p>
          <div className="flex gap-3">
            {['URL Phishing','Email Spam','Credential Risk','XAI Scoring'].map((t) => (
              <span key={t} className="text-xs px-3 py-1.5 rounded-full bg-panel2 border border-line text-accent">{t}</span>
            ))}
          </div>
        </div>
        <div className="text-xs text-muted">© 2026 RiskLens AI · Explainable Cyber Risk Intelligence</div>
      </div>

      <div className="flex items-center justify-center p-8">
        <div className="w-full max-w-sm">
          <h2 className="text-2xl font-bold mb-1">Welcome back</h2>
          <p className="text-muted text-sm mb-6">Sign in to your security dashboard.</p>
          <form onSubmit={submit} className="space-y-4">
            <div>
              <label className="label">Username or Email</label>
              <input className="input" value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} required />
            </div>
            <div>
              <label className="label">Password</label>
              <input className="input" type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} required />
            </div>
            {error && <p className="text-sm text-danger">{error}</p>}
            <button className="btn-primary w-full" disabled={loading}>{loading ? 'Signing in…' : 'Sign in'}</button>
          </form>
          <p className="text-sm text-muted mt-6 text-center">
            Don't have an account? <Link to="/register" className="text-accent font-semibold">Create one</Link>
          </p>
          <p className="text-xs text-muted mt-4 text-center">Demo admin: <span className="font-mono">admin / Admin@123456</span></p>
        </div>
      </div>
    </div>
  )
}