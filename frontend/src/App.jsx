import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './context/AuthContext'
import Layout from './components/Layout'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import UrlScan from './pages/UrlScan'
import EmailScan from './pages/EmailScan'
import CredentialScan from './pages/CredentialScan'
import Advisor from './pages/Advisor'
import Threats from './pages/Threats'
import Reports from './pages/Reports'
import Admin from './pages/Admin'

function Protected({ children }) {
  const { user } = useAuth()
  return user ? children : <Navigate to="/login" replace />
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route
        element={
          <Protected>
            <Layout />
          </Protected>
        }
      >
        <Route path="/" element={<Dashboard />} />
        <Route path="/url" element={<UrlScan />} />
        <Route path="/email" element={<EmailScan />} />
        <Route path="/credential" element={<CredentialScan />} />
        <Route path="/advisor" element={<Advisor />} />
        <Route path="/threats" element={<Threats />} />
        <Route path="/reports" element={<Reports />} />
        <Route path="/admin" element={<Admin />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}