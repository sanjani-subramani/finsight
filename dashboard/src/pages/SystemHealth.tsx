import { Fragment, useState } from 'react'
import {
  useWorkerHealth,
  useQueues,
  useDlq,
  useReplayDlq,
  useDeleteDlq,
  usePipelineMetrics,
  useShadowReport,
} from '../hooks/useAdmin'

export function SystemHealth() {
  const workerHealth = useWorkerHealth()
  const queues = useQueues()
  const dlq = useDlq()
  const replayDlq = useReplayDlq()
  const deleteDlq = useDeleteDlq()
  const pipelineMetrics = usePipelineMetrics()
  const shadowReport = useShadowReport()

  const [expandedDlq, setExpandedDlq] = useState<Set<string>>(new Set())

  function toggleDlq(id: string) {
    setExpandedDlq((prev) => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }

  const isHealthy = workerHealth.data?.status === 'healthy' || (workerHealth.data as any)?.healthy === true
  const latency = pipelineMetrics.data?.latency_p95_ms ?? pipelineMetrics.data?.simulation_duration_ms?.p95
  const isMetricsOk = pipelineMetrics.data?.health_status === 'healthy' || (latency != null && latency < 500)

  return (
    <div className="system-health-page">
      <h1>System Health</h1>

      <div className="stat-row">
        <div className={`glass-card ${isHealthy ? 'stat-card--ok' : 'stat-card--critical'}`} style={{ position: 'relative', overflow: 'hidden' }}>
          <div className="stat-card__label">
            <span className={`stat-card__dot stat-card__dot--${isHealthy ? 'ok' : 'critical'}`} />
            ARQ Worker Status
          </div>
          <div className="stat-card__value" style={{ textTransform: 'capitalize' }}>
            {workerHealth.data?.status ?? 'Unknown'}
          </div>
          <div className="stat-card__detail">
            {workerHealth.data?.last_heartbeat
              ? `Last heartbeat: ${workerHealth.data.seconds_since_heartbeat}s ago`
              : 'No heartbeat recorded'}
          </div>
        </div>

        <div className={`glass-card ${isMetricsOk ? 'stat-card--ok' : 'stat-card--warning'}`} style={{ position: 'relative', overflow: 'hidden' }}>
          <div className="stat-card__label">
            <span className={`stat-card__dot stat-card__dot--${isMetricsOk ? 'ok' : 'warning'}`} />
            Pipeline Latency
          </div>
          <div className="stat-card__value">
            {latency != null ? `${Number(latency).toFixed(1)} ms` : '—'}
          </div>
          <div className="stat-card__detail">95th percentile (last 24h)</div>
        </div>

        <div className="glass-card">
          <div className="stat-card__label">Shadow Precision</div>
          <div className="stat-card__value">
            {shadowReport.data?.human_alignment_score != null
              ? `${(shadowReport.data.human_alignment_score * 100).toFixed(1)}%`
              : '—'}
          </div>
          <div className="stat-card__detail">
            Model vs Human (last 30d)
          </div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 'var(--sp-6)', marginTop: 'var(--sp-6)' }}>
        <section>
          <h2>Stream Queues</h2>
          <div className="data-table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Topic</th>
                  <th>Length</th>
                  <th>Pending (Lag)</th>
                </tr>
              </thead>
              <tbody>
                {queues.isLoading && (
                  <tr className="data-table__skeleton">
                    <td><div className="data-table__skeleton-bar" /></td>
                    <td><div className="data-table__skeleton-bar" /></td>
                    <td><div className="data-table__skeleton-bar" /></td>
                  </tr>
                )}
                {queues.data?.map((q) => (
                  <tr key={q.topic}>
                    <td style={{ fontFamily: 'var(--font-mono)' }}>{q.topic}</td>
                    <td>{q.length}</td>
                    <td style={{ color: q.pending > 0 ? 'var(--color-warning)' : 'inherit' }}>
                      {q.pending}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <section>
          <h2>Dead Letter Queue (DLQ)</h2>
          <div className="data-table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Message ID</th>
                  <th>Topic</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {dlq.data?.length === 0 && (
                  <tr>
                    <td colSpan={3} className="data-table__empty">No messages in DLQ.</td>
                  </tr>
                )}
                {dlq.data?.map((msg) => (
                  <Fragment key={msg.message_id}>
                    <tr>
                      <td style={{ fontFamily: 'var(--font-mono)' }}>{msg.message_id}</td>
                      <td>{msg.payload?._topic ?? 'Unknown'}</td>
                      <td>
                        <div style={{ display: 'flex', gap: 'var(--sp-2)' }}>
                          <button
                            className="ghost"
                            onClick={() => toggleDlq(msg.message_id)}
                            style={{ padding: '4px 8px', fontSize: '0.75rem' }}
                          >
                            {expandedDlq.has(msg.message_id) ? 'Hide' : 'View'}
                          </button>
                          <button
                            className="secondary"
                            onClick={() => replayDlq.mutate(msg.message_id)}
                            disabled={replayDlq.isPending}
                            style={{ padding: '4px 8px', fontSize: '0.75rem', borderColor: 'var(--accent-primary)', color: 'var(--accent-primary-h)' }}
                          >
                            Replay
                          </button>
                          <button
                            className="ghost"
                            onClick={() => deleteDlq.mutate(msg.message_id)}
                            disabled={deleteDlq.isPending}
                            style={{ padding: '4px 8px', fontSize: '0.75rem', color: 'var(--color-critical)' }}
                          >
                            Drop
                          </button>
                        </div>
                      </td>
                    </tr>
                    {expandedDlq.has(msg.message_id) && (
                      <tr className="run-detail-table__expanded">
                        <td colSpan={3}>
                          <pre style={{
                            margin: 0, padding: 'var(--sp-3)', background: 'var(--bg-root)',
                            borderRadius: 'var(--radius-sm)', fontSize: '0.75rem', overflowX: 'auto'
                          }}>
                            {JSON.stringify(msg.payload, null, 2)}
                          </pre>
                        </td>
                      </tr>
                    )}
                  </Fragment>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </div>
  )
}
