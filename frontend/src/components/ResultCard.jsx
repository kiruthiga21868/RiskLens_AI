import { RiskBadge } from './ui.jsx'

export default function ResultCard({ result, kind }) {
  if (!result) return null
  const pos = kind === 'url' ? 'phishing' : kind === 'email' ? 'spam' : 'weak'
  const verdict = result.prediction === pos ? 'Threat detected' : 'Looks safe'

  return (
    <div className="card border-2" style={{ borderColor: result.prediction === pos ? '#ef444455' : '#22c55e55' }}>
      <div className="flex items-center justify-between mb-4">
        <div>
          <div className="text-muted text-xs uppercase tracking-wider font-semibold">Prediction</div>
          <div className="text-xl font-extrabold capitalize mt-0.5">
            {result.prediction} <span className="text-sm font-medium text-muted">· {verdict}</span>
          </div>
        </div>
        <div className="text-right">
          <div className="text-muted text-xs uppercase tracking-wider font-semibold">Confidence</div>
          <div className="text-xl font-extrabold">{(result.confidence * 100).toFixed(0)}%</div>
        </div>
      </div>

      <div className="grid sm:grid-cols-3 gap-4 mb-4">
        <div className="bg-panel2 rounded-lg p-3">
          <div className="text-xs text-muted">Risk Score</div>
          <div className="text-lg font-bold mt-1">{result.risk_score.toFixed(1)}</div>
        </div>
        <div className="bg-panel2 rounded-lg p-3 sm:col-span-2">
          <div className="text-xs text-muted mb-1">Raw model score</div>
          <div className="text-lg font-bold mt-1">{result.raw_score.toFixed(3)}</div>
        </div>
      </div>
      <div className="mb-3">
        <RiskBadge score={result.risk_score} />
      </div>

      <div className="space-y-4">
        <div>
          <div className="text-xs uppercase tracking-wider text-accent font-semibold mb-1">Explainable AI — Why?</div>
          <p className="text-sm text-ink/90 leading-relaxed">{result.explanation}</p>
        </div>
        <div>
          <div className="text-xs uppercase tracking-wider text-accent font-semibold mb-2">Feature Importance (SHAP)</div>
          <div className="space-y-1.5">
            {Object.entries(result.feature_importance)
              .sort((a, b) => Math.abs(b[1]) - Math.abs(a[1]))
              .slice(0, 6)
              .map(([name, val]) => (
                <div key={name} className="flex items-center gap-2 text-sm">
                  <span className="w-40 truncate text-muted">{name.replace(/_/g, ' ')}</span>
                  <div className="flex-1 h-2 bg-panel2 rounded-full overflow-hidden">
                    <div
                      className="h-full rounded-full"
                      style={{
                        width: `${Math.min(Math.abs(val) * 60, 100)}%`,
                        background: val >= 0 ? '#ef4444' : '#22c55e',
                      }}
                    />
                  </div>
                  <span className="w-16 text-right font-mono text-xs">{val >= 0 ? '+' : ''}{val.toFixed(2)}</span>
                </div>
              ))}
          </div>
        </div>
        <div>
          <div className="text-xs uppercase tracking-wider text-accent font-semibold mb-1">Personalized Recommendation</div>
          <p className="text-sm bg-accent/5 border border-accent/20 rounded-lg p-3 text-ink/90">{result.recommendation}</p>
        </div>
      </div>
    </div>
  )
}