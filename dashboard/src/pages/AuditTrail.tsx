import { useMemo, useState } from 'react'
import { useAuditLog } from '../hooks/useAudit'

const PAGE_SIZE = 30

const ACTION_ICONS: Record<string, string> = {
  'auth.login': '🔑',
  'auth.register': '👤',
  'auth.logout': '🚪',
  'auth.refresh': '🔄',
  'ingestion.manual_created': '📝',
  'ingestion.sms_created': '📱',
  'ingestion.csv_batch': '📊',
  'reconciliation.run_created': '⚖️',
  'reconciliation.result_resolved': '✅',
  'fingraph.node_added': '🔵',
  'fingraph.edge_added': '🔗',
  'fingraph.failure_simulated': '💥',
  'regimpact.regulation_ingested': '📜',
  'regimpact.rule_reviewed': '⚡',
  'regimpact.impact_analyzed': '📈',
  'threat.sms_analyzed': '🛡️',
  'threat.url_analyzed': '🔍',
  'threat.qr_analyzed': '📸',
  'threat.call_analyzed': '📞',
}

function getIcon(action: string): string {
  if (ACTION_ICONS[action]) return ACTION_ICONS[action]
  if (action.startsWith('auth.')) return '🔑'
  if (action.startsWith('ingestion.')) return '📝'
  if (action.startsWith('reconciliation.')) return '⚖️'
  if (action.startsWith('fingraph.')) return '🔵'
  if (action.startsWith('regimpact.')) return '📜'
  if (action.startsWith('threat.')) return '🛡️'
  return '📋'
}

function formatAction(action: string): string {
  return action.replace(/\./g, ' → ').replace(/_/g, ' ')
}

export function AuditTrail() {
  const [page, setPage] = useState(0)
  const [actionFilter, setActionFilter] = useState('')

  const filters = useMemo(() => ({
    action: actionFilter || undefined,
    limit: PAGE_SIZE,
    offset: page * PAGE_SIZE,
  }), [actionFilter, page])

  const query = useAuditLog(filters)
  const entries = query.data?.items ?? []
  const total = query.data?.total ?? 0

  return (
    <div className="audit-page">
      <h1>Audit Trail</h1>

      <div className="glass-card" style={{ marginBottom: 'var(--sp-4)', display: 'flex', alignItems: 'center', gap: 'var(--sp-4)', padding: 'var(--sp-4) var(--sp-5)' }}>
        <label style={{ flex: 1, flexDirection: 'row', alignItems: 'center', gap: 'var(--sp-3)' }}>
          <span style={{ fontSize: '0.75rem', whiteSpace: 'nowrap' }}>Filter by action:</span>
          <input
            type="text"
            value={actionFilter}
            onChange={(e) => { setActionFilter(e.target.value); setPage(0) }}
            placeholder="e.g. auth.login, ingestion, threat..."
            style={{ maxWidth: 300 }}
          />
        </label>
        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
          {total} entries
        </span>
      </div>

      {query.isLoading && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--sp-2)' }}>
          {Array.from({ length: 8 }, (_, i) => (
            <div key={i} className="skeleton" style={{ height: 52 }} />
          ))}
        </div>
      )}

      <div style={{ position: 'relative', paddingLeft: 'var(--sp-8)' }}>
        {/* Timeline line */}
        <div style={{
          position: 'absolute', left: 14, top: 4, bottom: 4,
          width: 2, background: 'var(--border-default)',
        }} />

        {entries.map((entry, i) => (
          <div
            key={entry.id}
            className="animate-fade-in"
            style={{
              position: 'relative', marginBottom: 'var(--sp-3)',
              animationDelay: `${i * 30}ms`,
            }}
          >
            {/* Timeline dot */}
            <div style={{
              position: 'absolute', left: 'calc(var(--sp-8) * -1 + 8px)', top: 14,
              width: 14, height: 14, borderRadius: 'var(--radius-full)',
              background: 'var(--bg-surface)', border: '2px solid var(--accent-primary)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: '0.5rem',
            }} />

            <div style={{
              background: 'var(--bg-card)', border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-md)', padding: 'var(--sp-3) var(--sp-4)',
              display: 'flex', alignItems: 'center', gap: 'var(--sp-3)',
              transition: 'border-color var(--transition-fast)',
            }}
              onMouseEnter={(e) => (e.currentTarget.style.borderColor = 'rgba(148,163,184,0.25)')}
              onMouseLeave={(e) => (e.currentTarget.style.borderColor = 'var(--border-subtle)')}
            >
              <span style={{ fontSize: '1rem', flexShrink: 0 }}>{getIcon(entry.action)}</span>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontSize: '0.8125rem', fontWeight: 500, color: 'var(--text-primary)' }}>
                  {formatAction(entry.action)}
                </div>
                <div style={{ fontSize: '0.6875rem', color: 'var(--text-muted)', display: 'flex', gap: 'var(--sp-3)', flexWrap: 'wrap' }}>
                  {entry.actor_email && <span>{entry.actor_email}</span>}
                  {entry.resource_type && <span>• {entry.resource_type}{entry.resource_id ? `: ${entry.resource_id.substring(0, 8)}…` : ''}</span>}
                  {entry.ip_address && <span>• {entry.ip_address}</span>}
                </div>
              </div>
              <div style={{ fontSize: '0.6875rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', whiteSpace: 'nowrap', flexShrink: 0 }}>
                {new Date(entry.created_at).toLocaleString()}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Pagination */}
      {total > PAGE_SIZE && (
        <div style={{ display: 'flex', justifyContent: 'center', gap: 'var(--sp-3)', marginTop: 'var(--sp-6)' }}>
          <button className="secondary" disabled={page === 0} onClick={() => setPage((p) => p - 1)}>
            ← Previous
          </button>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', fontFamily: 'var(--font-mono)' }}>
            {page * PAGE_SIZE + 1}–{Math.min((page + 1) * PAGE_SIZE, total)} of {total}
          </span>
          <button className="secondary" disabled={(page + 1) * PAGE_SIZE >= total} onClick={() => setPage((p) => p + 1)}>
            Next →
          </button>
        </div>
      )}

      {entries.length === 0 && !query.isLoading && (
        <div style={{ textAlign: 'center', padding: 'var(--sp-10)', color: 'var(--text-muted)' }}>
          No audit entries found.
        </div>
      )}
    </div>
  )
}
