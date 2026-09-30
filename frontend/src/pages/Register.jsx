import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Register() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ username: '', email: '', full_name: '', password: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const submit = async (e) => {
    e.preventDefault()
    if (form.password.length < 8) return setError('Password must be at least 8 characters.')
    setLoading(true); setError('')
    try {
      await register(form)
      navigate('/')
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed')
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
        <h1 className="text-4xl font-extrabold leading-tight">Your personal<br />security assistant,<br /> powered by AI.</h1>
        <div className="text-xs text-muted">© 2026 RiskLens AI</div>
      </div>

      <div className="flex items-center justify-center p-8">
        <div className="w-full max-w-sm">
          <h2 className="text-2xl font-bold mb-1">Create account</h2>
          <p className="text-muted text-sm mb-6">Start your cyber health journey.</p>
          <form onSubmit={submit} className="space-y-4">
            <div>
              <label className="label">Full name</label>
              <input className="input" value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} />
            </div>
            <div>
              <label className="label">Username</label>
              <input className="input" value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} required />
            </div>
            <div>
              <label className="label">Email</label>
              <input className="input" type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required />
            </div>
            <div>
              <label className="label">Password (min 8 chars)</label>
              <input className="input" type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} required />
            </div>
            {error && <p className="text-sm text-danger">{error}</p>}
            <button className="btn-primary w-full" disabled={loading}>{loading ? 'Creating…' : 'Create account'}</button>
          </form>
          <p className="text-sm text-muted mt-6 text-center">
            Already registered? <Link to="/login" className="text-accent font-semibold">Sign in</Link>
          </p>
        </div>
      </div>
    </div>
  )
}