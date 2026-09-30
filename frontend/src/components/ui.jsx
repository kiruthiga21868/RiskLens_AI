export function riskColor(score) {
  if (score >= 70) return '#ef4444'
  if (score >= 40) return '#f59e0b'
  return '#22c55e'
}

export function riskLabel(score) {
  if (score >= 70) return 'High Risk'
  if (score >= 40) return 'Medium Risk'
  return 'Low Risk'
}

export function RiskBadge({ score }) {
  const c = riskColor(score)
  return (
    <span
      className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold"
      style={{ color: c, background: `${c}1a`, border: `1px solid ${c}55` }}
    >
      <span className="w-1.5 h-1.5 rounded-full" style={{ background: c }} />
      {riskLabel(score)}
    </span>
  )
}

export function Gauge({ score }) {
  const c = riskColor(score)
  const angle = (score / 100) * 180
  return (
    <div className="relative w-40 h-24 overflow-hidden">
      <div
        className="w-40 h-40 rounded-full"
        style={{
          background: `conic-gradient(${c} ${angle}deg, #1f2d48 ${angle}deg)`,
          transform: 'rotate(180deg)',
        }}
      />
      <div className="absolute inset-x-0 bottom-0 h-20 bg-base" />
      <div className="absolute bottom-0 inset-x-0 text-center">
        <div className="text-4xl font-extrabold text-ink leading-none">{Math.round(score)}</div>
        <div className="text-[11px] text-muted mt-1 uppercase tracking-wider">{riskLabel(score)}</div>
      </div>
    </div>
  )
}

export function StatCard({ label, value, sub, tone = 'text-ink' }) {
  return (
    <div className="card">
      <div className="text-xs uppercase tracking-wider text-muted font-semibold">{label}</div>
      <div className={`mt-2 text-2xl font-extrabold ${tone}`}>{value}</div>
      {sub && <div className="mt-1 text-xs text-muted">{sub}</div>}
    </div>
  )
}