import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const NAV = [
  { to: '/', label: 'Dashboard', icon: 'M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z' },
  { to: '/url', label: 'URL Scanner', icon: 'M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10 10-4.5 10-10S17.5 2 12 2zm0 18c-4.4 0-8-3.6-8-8s3.6-8 8-8 8 3.6 8 8-3.6 8-8 8zM8 8h8v2H8zm0 4h8v2H8zm0 4h5v2H8z' },
  { to: '/email', label: 'Email Analyzer', icon: 'M20 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z' },
  { to: '/credential', label: 'Credential Risk', icon: 'M18 8h-1V6c0-2.8-2.2-5-5-5S7 3.2 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zm-6 9c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zm3.1-9H8.9V6c0-1.7 1.4-3.1 3.1-3.1 1.7 0 3.1 1.4 3.1 3.1v2z' },
  { to: '/advisor', label: 'AI Advisor', icon: 'M12 3c-4.4 0-8 3.1-8 7 0 1.9.8 3.6 2.1 4.9L5 20l4.2-2.1c.9.3 1.8.4 2.8.4 4.4 0 8-3.1 8-7s-3.6-7-8-7z' },
  { to: '/threats', label: 'Threat History', icon: 'M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10 10-4.5 10-10S17.5 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z' },
  { to: '/reports', label: 'Reports', icon: 'M6 2c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V8l-6-6H6zm7 7V3.5L18.5 9H13zm-2 9v-4h2v4h-2zm4 0v-8h2v8h-2zm-8 0v-6h2v6H7z' },
  { to: '/admin', label: 'Admin', icon: 'M12 12c2.2 0 4-1.8 4-4s-1.8-4-4-4-4 1.8-4 4 1.8 4 4 4zm0 2c-2.7 0-8 1.3-8 4v2h16v-2c0-2.7-5.3-4-8-4z' },
]

export default function Layout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  return (
    <div className="flex min-h-screen">
      {/* Sidebar */}
      <aside className="w-60 shrink-0 bg-panel border-r border-line flex flex-col sticky top-0 h-screen">
        <div className="px-5 py-5 border-b border-line">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-accent/20 border border-accent/40 grid place-items-center">
              <span className="text-accent font-extrabold">R</span>
            </div>
            <div>
              <div className="font-bold leading-none text-ink">RiskLens AI</div>
              <div className="text-[10px] text-muted mt-1">Cyber Risk Intelligence</div>
            </div>
          </div>
        </div>

        <nav className="flex-1 py-4 px-3 space-y-1 overflow-y-auto">
          {NAV.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition ${
                  isActive
                    ? 'bg-accent/15 text-accent border border-accent/30'
                    : 'text-muted hover:bg-panel2 hover:text-ink border border-transparent'
                }`
              }
            >
              <svg className="w-5 h-5 shrink-0" fill="currentColor" viewBox="0 0 24 24">
                <path d={item.icon} />
              </svg>
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="p-4 border-t border-line">
          <div className="text-xs font-semibold text-ink truncate">{user?.full_name || user?.username}</div>
          <div className="text-[11px] text-muted mb-2">{user?.email}</div>
          <button
            onClick={() => { logout(); navigate('/login') }}
            className="text-xs text-muted hover:text-danger transition w-full text-left"
          >
            Sign out
          </button>
        </div>
      </aside>

      {/* Main */}
      <main className="flex-1 p-8 max-w-7xl">
        <Outlet />
      </main>
    </div>
  )
}