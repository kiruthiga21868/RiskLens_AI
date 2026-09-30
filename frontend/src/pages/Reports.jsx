import api from '../api/client'

export default function Reports() {
  const download = async (kind) => {
    const { data } = await api.get(`/reports/${kind}`, { responseType: 'blob' })
    const url = URL.createObjectURL(data)
    const a = document.createElement('a')
    a.href = url
    a.download = `risklens_report.${kind}`
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="space-y-6 max-w-3xl">
      <div>
        <h1 className="text-2xl font-bold">Security Reports</h1>
        <p className="text-muted text-sm">Download your threat summary, health score and recommendations.</p>
      </div>

      <div className="grid sm:grid-cols-2 gap-4">
        <div className="card">
          <div className="text-lg font-bold mb-1">PDF Report</div>
          <p className="text-sm text-muted mb-4">Branded PDF with cyber health score, component breakdown and recent assessments.</p>
          <button className="btn-primary" onClick={() => download('pdf')}>Download PDF</button>
        </div>
        <div className="card">
          <div className="text-lg font-bold mb-1">CSV Export</div>
          <p className="text-sm text-muted mb-4">Raw threat history in CSV for spreadsheets and further analysis.</p>
          <button className="btn-ghost" onClick={() => download('csv')}>Download CSV</button>
        </div>
      </div>
    </div>
  )
}