import { useEffect, useState } from 'react'
import api from '../api/client'
import { StatCard } from '../components/ui'
import { useAuth } from '../context/AuthContext'
import { Navigate } from 'react-router-dom'

export default function Admin() {
  const { user } = useAuth()
  const [stats, setStats] = useState(null)
  const [users, setUsers] = useState([])
  const [error, setError] = useState('')

  useEffect(() => {
    api.get('/admin/stats').then((r) => setStats(r.data)).catch((e) => setError(e.response?.data?.detail || 'Access denied'))
    api.get('/admin/users').then((r) => setUsers(r.data)).catch(() => {})
  }, [])

  if (user?.role !== 'admin') return <Navigate to="/" replace />
  if (error) return <p className="text-danger">{error}</p>
  if (!stats) return <p className="text-muted">Loading platform stats…</p>

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Admin Dashboard</h1>
        <p className="text-muted text-sm">Platform-wide oversight.</p>
      </div>

      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard label="Users" value={stats.total_users} />
        <StatCard label="Total Scans" value={stats.total_scans} />
        <StatCard label="High-Risk Scans" value={stats.high_risk_scans} tone="text-danger" />
        <StatCard label="Avg Health Score" value={stats.avg_health_score} tone="text-ok" />
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        <div className="card">
          <div className="text-sm font-semibold mb-4">Scans by Type</div>
          <div className="space-y-2">
            {Object.entries(stats.scans_by_type).map(([type, count]) => (
              <div key={type} className="flex items-center justify-between text-sm">
                <span className="capitalize text-ink/90">{type}</span>
                <div className="flex-1 mx-4 h-2 bg-panel2 rounded-full overflow-hidden">
                  <div className="h-full bg-accent rounded-full" style={{ width: `${Math.min((count / Math.max(stats.total_scans, 1)) * 100, 100)}%` }} />
                </div>
                <span className="font-semibold">{count}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="card">
          <div className="text-sm font-semibold mb-4">Registered Users</div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-muted text-xs uppercase">
                  <th className="pb-2">Username</th>
                  <th className="pb-2">Email</th>
                  <th className="pb-2">Role</th>
                  <th className="pb-2">Awareness</th>
                </tr>
              </thead>
              <tbody>
                {users.map((u) => (
                  <tr key={u.id} className="border-t border-line/50">
                    <td className="py-2 text-ink/90">{u.username}</td>
                    <td className="py-2 text-muted">{u.email}</td>
                    <td className="py-2">
                      <span className={`px-2 py-0.5 rounded text-xs font-semibold ${u.role === 'admin' ? 'bg-accent/15 text-accent' : 'bg-panel2 text-muted'}`}>{u.role}</span>
                    </td>
                    <td className="py-2 text-muted">{u.awareness_score}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}