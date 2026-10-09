import { useTransactionDetail } from '../../hooks/usePaytrace'
import { ConfidenceBadge } from '../shared/ConfidenceBadge'
import './TransactionDrawer.css'

export interface TransactionDrawerProps {
  orgId: string
  transactionRef: string
  onClose: () => void
}

/**
 * TRANSACTION TIMELINE -- the visual proof of PayTrace's event-sourcing
 * work (Step 14): the folded event sequence rendered as a vertical
 * stepper (stage, timestamp, latency since the previous stage), not a
 * raw JSON dump of TransactionState. The FailureClassification is shown
 * prominently above it, including recommended_action, since that's the
 * actionable answer an ops engineer opened this drawer for.
 */
export function TransactionDrawer({ orgId, transactionRef, onClose }: TransactionDrawerProps) {
  const { data, isLoading } = useTransactionDetail(orgId, transactionRef)

  return (
    <div className="txn-drawer__backdrop" onClick={onClose}>
      <aside className="txn-drawer" onClick={(e) => e.stopPropagation()} aria-label="Transaction detail">
        <header className="txn-drawer__header">
          <h2>{transactionRef}</h2>
          <button type="button" onClick={onClose} aria-label="Close">
            ×
          </button>
        </header>

        {isLoading && <p>Loading…</p>}

        {data && (
          <>
            <section className="txn-drawer__classification">
              <div className="txn-drawer__classification-mode">{data.classification.mode.replace(/_/g, ' ')}</div>
              <ConfidenceBadge value={data.classification.confidence} label="Confidence" />
              <p>{data.classification.human_summary}</p>
              {data.classification.recommended_action && (
                <p className="txn-drawer__action">
                  <strong>Recommended action:</strong> {data.classification.recommended_action}
                </p>
              )}
            </section>

            <ol className="txn-drawer__stepper">
              {data.state.timeline.map((entry, i) => {
                const prev = data.state.timeline[i - 1]
                const latencyMs = prev
                  ? new Date(entry.occurred_at).getTime() - new Date(prev.occurred_at).getTime()
                  : null
                return (
                  <li key={`${entry.stage}-${entry.occurred_at}`} className="txn-drawer__step">
                    <div className="txn-drawer__step-marker" aria-hidden="true" />
                    <div className="txn-drawer__step-body">
                      <div className="txn-drawer__step-stage">{entry.stage.replace(/_/g, ' ')}</div>
                      <div className="txn-drawer__step-meta">
                        {new Date(entry.occurred_at).toLocaleString()}
                        {latencyMs !== null && <span> · +{latencyMs}ms since previous stage</span>}
                      </div>
                      {entry.error_code && <div className="txn-drawer__step-error">error: {entry.error_code}</div>}
                    </div>
                  </li>
                )
              })}
            </ol>

            {data.state.anomalies.length > 0 && (
              <section className="txn-drawer__anomalies">
                <h3>Anomalies</h3>
                <ul>
                  {data.state.anomalies.map((a, i) => (
                    <li key={i}>{a.description}</li>
                  ))}
                </ul>
              </section>
            )}
          </>
        )}
      </aside>
    </div>
  )
}
