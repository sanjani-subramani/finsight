import { Navigate, Route, BrowserRouter as Router, Routes } from 'react-router-dom'
import { OrgAuthProvider } from './auth/OrgAuthContext'
import { useOrgAuth } from './auth/useOrgAuth'
import { Shell } from './components/layout/Shell'
import { Compliance } from './pages/Compliance'
import { Dependencies } from './pages/Dependencies'
import { Login } from './pages/Login'
import { Overview } from './pages/Overview'
import { Payments } from './pages/Payments'
import { Reconciliation } from './pages/Reconciliation'
import { ThreatIntelligence } from './pages/ThreatIntelligence'
import { RequireRole } from './auth/RequireRole'
import { AuditTrail } from './pages/AuditTrail'
import { SystemHealth } from './pages/SystemHealth'

function ProtectedShell() {
  const { isAuthenticated, isLoading } = useOrgAuth()

  if (isLoading) return <p>Loading…</p>
  if (!isAuthenticated) return <Navigate to="/login" replace />
  return <Shell />
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route element={<ProtectedShell />}>
        <Route index element={<Overview />} />
        <Route path="/payments" element={<Payments />} />
        <Route path="/reconciliation" element={<Reconciliation />} />
        <Route path="/dependencies" element={<Dependencies />} />
        <Route path="/compliance" element={<Compliance />} />
        <Route path="/threats" element={<ThreatIntelligence />} />
        <Route
          path="/audit"
          element={
            <RequireRole roles={['owner', 'ops_engineer']}>
              <AuditTrail />
            </RequireRole>
          }
        />
        <Route
          path="/system"
          element={
            <RequireRole roles={['owner', 'ops_engineer']}>
              <SystemHealth />
            </RequireRole>
          }
        />
      </Route>
    </Routes>
  )
}

function App() {
  return (
    <Router>
      <OrgAuthProvider>
        <AppRoutes />
      </OrgAuthProvider>
    </Router>
  )
}

export default App
