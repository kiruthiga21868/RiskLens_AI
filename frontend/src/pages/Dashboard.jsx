import { useEffect, useState } from 'react'
import {
  Chart as ChartJS, ArcElement, CategoryScale, LinearScale, BarElement, PointElement, LineElement, Tooltip, Legend, Filler,
} from 'chart.js'
import { Line, Doughnut, Bar } from 'react-chartjs-2'
import api from '../api/client'
import { Gauge, StatCard, RiskBadge } from '../components/ui'
import { riskColor } from '../components/ui'

ChartJS.register(ArcElement, CategoryScale, LinearScale, BarElement, PointElement, LineElement, Tooltip, Legend, Filler)

export default function Dashboard() {
  const [data, setData] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api.get('/dashboard').then((r) => setData(r.data)).catch(() => setError('Failed to load dashboard'))
  }, [])

  if (error) return <p className="text-danger">{error}</p>
  if (!data) return <p className="text-muted">Loading security posture…</p>

  const lineData = {
    labels: (data.last_30d || []).map((d) => d.date?.slice(5) ?? ''),
    datasets: [
      {
        label: 'Avg Risk',
        data: (data.last_30d || []).map((d) => d.avg_risk),
        borderColor: '#ef4444',
        backgroundColor: 'rgba(239,68,68,0.08)',
        fill: true,
        tension: 0.4,
      },
    ],
  }

  const donutData = {
    labels: ['URL', 'Email', 'Credential'],
    datasets: [
      {
        data: (data.threat_summary || []).map((t) => t.count),
        backgroundColor: ['#38bdf8', '#f59e0b', '#a78bfa'],
        borderWidth: 0,
      },
    ],
  }

  const comps = data.components || {}
  const bars = {
    labels: ['URL Safety', 'Spam Exposure', 'Credential Strength', 'Awareness', 'Threat History'],
    datasets: [
      {
        label: 'Score',
        data: [comps.url_safety, comps.spam_exposure, comps.credential_strength, comps.awareness_score, comps.threat_history],
        backgroundColor: ['#38bdf8', '#f59e0b', '#a78bfa', '#22c55e', '#f43f5e'],
        borderRadius: 6,
      },
    ],
  }

  const trend = data.trend === 'improving' ? 'text-ok' : data.trend === 'declining' ? 'text-danger' : 'text-muted'

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Security Dashboard</h1>
          <p className="text-muted text-sm">Your live cyber risk posture overview.</p>
        </div>
        <span className={`text-sm font-semibold capitalize ${trend}`}>● {data.trend}</span>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        <div className="card flex items-center gap-6">
          <Gauge score={data.health_score} />
          <div>
            <div className="text-xs uppercase text-muted font-semibold">Cyber Health Score</div>
            <div className="text-3xl font-extrabold mt-1" style={{ color: riskColor(data.health_score) }}>
              {data.health_score.toFixed(1)}
            </div>
            <div className="text-sm text-muted mt-1">Status: <span className="text-ink font-semibold">{data.status}</span></div>
          </div>
        </div>
        <StatCard label="Total Scans" value={data.total_scans} sub="Across all modules" />
        <div className="card">
          <div className="text-xs uppercase tracking-wider text-muted font-semibold mb-2">Scans by Module</div>
          <div className="h-40"><Doughnut data={donutData} options={{ cutout: '62%', plugins: { legend: { position: 'bottom', labels: { color: '#94a3b8' } } } }} /></div>
        </div>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        <div className="card">
          <div className="text-sm font-semibold mb-4">Risk Trend — Last 30 Days</div>
          <div className="h-56"><Line data={lineData} options={{ plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, max: 100, grid: { color: '#1f2d48' } }, x: { grid: { color: 'transparent' } } } }} /></div>
        </div>
        <div className="card">
          <div className="text-sm font-semibold mb-4">Health Components</div>
          <div className="h-56"><Bar data={bars} options={{ plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, max: 100, grid: { color: '#1f2d48' } }, x: { grid: { color: 'transparent' } } } }} /></div>
        </div>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        <div className="card">
          <div className="text-sm font-semibold mb-4">Recent Activity</div>
          <div className="space-y-3">
            {(data.recent_activity || []).slice(0, 6).map((a) => (
              <div key={a.id} className="flex items-center justify-between text-sm border-b border-line/60 pb-2 last:border-0">
                <div>
                  <span className="uppercase text-xs font-bold text-accent px-2 py-0.5 rounded bg-accent/10 mr-2">{a.type}</span>
                  <span className="text-ink/90">{a.content.slice(0, 46)}…</span>
                </div>
                <RiskBadge score={a.risk_score} />
              </div>
            ))}
            {data.recent_activity?.length === 0 && <p className="text-muted text-sm">No scans yet — try the URL scanner.</p>}
          </div>
        </div>
        <div className="card">
          <div className="text-sm font-semibold mb-4">Threat Summary</div>
          <div className="space-y-3">
            {(data.threat_summary || []).map((t) => (
              <div key={t.type} className="flex items-center justify-between text-sm">
                <span className="capitalize text-ink/90">{t.type}</span>
                <div className="flex gap-3">
                  <span className="text-ok font-semibold">{t.low} low</span>
                  <span className="text-warn font-semibold">{t.medium} med</span>
                  <span className="text-danger font-semibold">{t.high} high</span>
                  <span className="text-muted w-12 text-right">avg {t.avg_risk}</span>
                </div>
              </div>
            ))}
            {data.threat_summary?.length === 0 && <p className="text-muted text-sm">No threat data yet.</p>}
          </div>
        </div>
      </div>
    </div>
  )
}