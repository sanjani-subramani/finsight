import { useQueries } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { fingraphApi } from '../api/fingraph'
import { paytraceApi } from '../api/paytrace'
import { reconxApi } from '../api/reconx'
import { regimpactApi } from '../api/regimpact'
import { useOrgAuth } from '../auth/useOrgAuth'
import { StatCard } from '../components/shared/StatCard'
import { useAuditLog } from '../hooks/useAudit'
import { useQueues, useWorkerHealth } from '../hooks/useAdmin'

const ACTION_ICONS: Record<string, string> = {
  'auth.login': '🔑',
  'auth.register': '👤',
  'ingestion.manual_created': '📝',
  'ingestion.sms_created': '📱',
  'reconciliation.run_created': '⚖️',
  'reconciliation.result_resolved': '✅',
  'fingraph.node_added': '🔵',
  'fingraph.failure_simulated': '💥',
  'regimpact.rule_reviewed': '⚡',
  'threat.sms_analyzed': '🛡️',
  'threat.url_analyzed': '🔍',
}

function getActionIcon(action: string): string {
  if (ACTION_ICONS[action]) return ACTION_ICONS[action]
  if (action.startsWith('auth.')) return '🔑'
  if (action.startsWith('ingestion.')) return '📝'
  if (action.startsWith('reconciliation.')) return '⚖️'
  if (action.startsWith('fingraph.')) return '🔵'
  if (action.startsWith('regimpact.')) return '📜'
  if (action.startsWith('threat.')) return '🛡️'
  return '📋'
}

export function Overview() {
  const { currentOrgId, user } = useOrgAuth()
  const orgId = currentOrgId as string

  const [healthQuery, alertsQuery, runsQuery, graphQuery, criticalQuery, pendingRulesQuery] = useQueries({
    queries: [
      { queryKey: ['overview', 'health', orgId], queryFn: () => paytraceApi.getHealth(orgId), enabled: !!orgId },
      { queryKey: ['overview', 'alerts', orgId], queryFn: () => paytraceApi.getAlerts(orgId), enabled: !!orgId },
      { queryKey: ['overview', 'runs', orgId], queryFn: () => reconxApi.listRuns(orgId), enabled: !!orgId },
      { queryKey: ['overview', 'graph', orgId], queryFn: () => fingraphApi.getGraph(orgId), enabled: !!orgId },
      {
        queryKey: ['overview', 'critical', orgId],
        queryFn: () => fingraphApi.getCriticalNodes(orgId),
        enabled: !!orgId,
      },
      {
        queryKey: ['overview', 'pending-rules', orgId],
        queryFn: () => regimpactApi.getPendingRules(orgId),
        enabled: !!orgId,
      },
    ],
  })

  const auditQuery = useAuditLog({ limit: 6 })
  const workerHealth = useWorkerHealth()
  const queues = useQueues()

  const latestRun = runsQuery.data?.[0]
  const cycleCount = graphQuery.data?.cycle_warnings.length ?? 0
  const criticalCount = criticalQuery.data?.filter((c) => c.is_critical).length ?? 0
  const activeAlerts = alertsQuery.data?.length ?? 0
  const isWorkerHealthy = workerHealth.data?.status === 'healthy' || (workerHealth.data as any)?.healthy === true

  if (!orgId) {
    return <p>Select an organization to see its dashboard.</p>
  }

  const currentDateStr = new Date().toLocaleDateString(undefined, {
    weekday: 'long',
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })

  return (
    <div className="overview-page">
      <div className="overview-header" style={{ marginBottom: 'var(--sp-6)', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 'var(--sp-4)' }}>
        <div>
          <h1 style={{ marginBottom: 'var(--sp-1)' }}>
            Welcome back{user?.email ? `, ${user.email.split('@')[0]}` : ''}
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.8125rem' }}>
            {currentDateStr} • Operational overview and telemetry
          </p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--sp-3)' }}>
          <div className="glass-card" style={{ padding: 'var(--sp-2) var(--sp-4)', display: 'flex', alignItems: 'center', gap: 'var(--sp-2)', borderRadius: 'var(--radius-full)' }}>
            <span
              style={{
                width: 8,
                height: 8,
                borderRadius: '50%',
                background: isWorkerHealthy ? 'var(--color-success)' : 'var(--color-warning)',
                boxShadow: isWorkerHealthy ? '0 0 8px rgba(16, 185, 129, 0.7)' : '0 0 8px rgba(245, 158, 11, 0.7)',
                animation: 'pulse 2s infinite',
              }}
            />
            <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
              {isWorkerHealthy ? 'Pipeline Active' : 'Pipeline Warning'}
            </span>
          </div>
        </div>
      </div>

      <section style={{ marginBottom: 'var(--sp-8)' }}>
        <h2 style={{ fontSize: '0.875rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 'var(--sp-3)' }}>
          Core Metrics
        </h2>
        <div className="stat-row">
          <StatCard
            label="Payment Success Rate"
            value={healthQuery.data ? `${(healthQuery.data.success_rate * 100).toFixed(1)}%` : '—'}
            severity={healthQuery.data && healthQuery.data.success_rate < 0.9 ? 'warning' : 'ok'}
            detail={activeAlerts > 0 ? `${activeAlerts} active provider alert(s)` : 'All payment rails operational'}
            href="/payments"
          />
          <StatCard
            label="Reconciliation Match"
            value={latestRun ? `${((latestRun.matched / Math.max(latestRun.total_records, 1)) * 100).toFixed(1)}%` : '—'}
            severity={latestRun && latestRun.unresolved > 0 ? 'warning' : 'ok'}
            detail={latestRun ? `${latestRun.unresolved} unresolved item(s)` : 'No recent runs'}
            href="/reconciliation"
          />
          <StatCard
            label="Critical Dependencies"
            value={criticalCount}
            severity={cycleCount > 0 ? 'critical' : 'ok'}
            detail={cycleCount > 0 ? `${cycleCount} dependency cycle detected!` : 'Dependency graph healthy'}
            href="/dependencies"
          />
          <StatCard
            label="Pending Compliance"
            value={pendingRulesQuery.data?.length ?? '—'}
            severity={(pendingRulesQuery.data?.length ?? 0) > 0 ? 'warning' : 'ok'}
            detail="Rules awaiting engineer review"
            href="/compliance"
          />
        </div>
      </section>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: 'var(--sp-6)' }}>
        {/* Recent Activity from Audit Trail */}
        <section className="glass-card" style={{ padding: 'var(--sp-5)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--sp-4)' }}>
            <h2 style={{ margin: 0, fontSize: '1rem', fontWeight: 600 }}>Recent Activity</h2>
            <Link to="/audit" style={{ fontSize: '0.75rem', color: 'var(--accent-primary-h)', textDecoration: 'none' }}>
              View all →
            </Link>
          </div>

          {auditQuery.isLoading && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--sp-2)' }}>
              {[1, 2, 3, 4].map((n) => (
                <div key={n} className="skeleton" style={{ height: 44 }} />
              ))}
            </div>
          )}

          {(!auditQuery.data?.items || auditQuery.data.items.length === 0) && !auditQuery.isLoading && (
            <p style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>No recent activity logged.</p>
          )}

          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--sp-2)' }}>
            {(auditQuery.data?.items ?? []).map((entry) => (
              <div
                key={entry.id}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 'var(--sp-3)',
                  padding: 'var(--sp-2) var(--sp-3)',
                  borderRadius: 'var(--radius-md)',
                  background: 'var(--bg-card)',
                  border: '1px solid var(--border-subtle)',
                  fontSize: '0.8125rem',
                }}
              >
                <span style={{ fontSize: '1rem' }}>{getActionIcon(entry.action)}</span>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontWeight: 500, color: 'var(--text-primary)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {entry.action.replace(/\./g, ' → ').replace(/_/g, ' ')}
                  </div>
                  <div style={{ fontSize: '0.6875rem', color: 'var(--text-muted)' }}>
                    {entry.actor_email ?? 'System'}
                  </div>
                </div>
                <span style={{ fontSize: '0.6875rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', whiteSpace: 'nowrap' }}>
                  {new Date(entry.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </span>
              </div>
            ))}
          </div>
        </section>

        {/* System & Pipeline Health Mini-Widget */}
        <section className="glass-card" style={{ padding: 'var(--sp-5)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--sp-4)' }}>
            <h2 style={{ margin: 0, fontSize: '1rem', fontWeight: 600 }}>Pipeline &amp; Stream Health</h2>
            <Link to="/system" style={{ fontSize: '0.75rem', color: 'var(--accent-primary-h)', textDecoration: 'none' }}>
              System console →
            </Link>
          </div>

          <div style={{ display: 'flex', gap: 'var(--sp-3)', marginBottom: 'var(--sp-4)' }}>
            <div style={{ flex: 1, padding: 'var(--sp-3)', background: 'var(--bg-card)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
              <div style={{ fontSize: '0.6875rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Worker Status</div>
              <div style={{ fontSize: '0.9375rem', fontWeight: 600, color: isWorkerHealthy ? 'var(--color-success)' : 'var(--color-warning)', marginTop: 2 }}>
                {isWorkerHealthy ? 'Healthy' : 'Unhealthy'}
              </div>
            </div>
            <div style={{ flex: 1, padding: 'var(--sp-3)', background: 'var(--bg-card)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
              <div style={{ fontSize: '0.6875rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Active Streams</div>
              <div style={{ fontSize: '0.9375rem', fontWeight: 600, color: 'var(--text-primary)', marginTop: 2 }}>
                {queues.data?.length ?? 0} queues
              </div>
            </div>
          </div>

          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: 'var(--sp-2)' }}>
            Stream queue depths:
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--sp-2)' }}>
            {(queues.data ?? []).slice(0, 4).map((q) => (
              <div
                key={q.topic}
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: 'var(--sp-2) var(--sp-3)',
                  background: 'var(--bg-card)',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: '0.75rem',
                  fontFamily: 'var(--font-mono)',
                }}
              >
                <span style={{ color: 'var(--text-secondary)' }}>{q.topic}</span>
                <span style={{ color: q.pending > 0 ? 'var(--color-warning)' : 'var(--text-muted)' }}>
                  {q.length} msg {q.pending > 0 ? `(${q.pending} lag)` : ''}
                </span>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  )
}
