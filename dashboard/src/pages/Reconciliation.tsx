import { Fragment, useMemo, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { RequireRole } from '../auth/RequireRole'
import { useOrgAuth } from '../auth/useOrgAuth'
import { NewRunPanel } from '../components/reconciliation/NewRunPanel'
import { ReconStatusBadge } from '../components/reconciliation/ReconStatusBadge'
import { ResolveModal } from '../components/reconciliation/ResolveModal'
import { ConfidenceBadge } from '../components/shared/ConfidenceBadge'
import { FilterBar } from '../components/shared/FilterBar'
import { useReconRun, useReconRuns, useResolveReconResult } from '../hooks/useReconx'
import type { ReconStatus, ReconciliationResult } from '../types/reconx'

const STATUS_OPTIONS: { value: ReconStatus; label: string }[] = [
  'matched',
  'missing_in_bank',
  'missing_in_gateway',
  'missing_in_internal',
  'duplicate',
  'amount_mismatch',
  'timing_difference',
  'unresolved',
].map((value) => ({ value: value as ReconStatus, label: value.replace(/_/g, ' ') }))

export function Reconciliation() {
  const { currentOrgId } = useOrgAuth()
  const orgId = currentOrgId as string
  const [selectedRunId, setSelectedRunId] = useState<string | null>(null)
  const [expanded, setExpanded] = useState<Set<string>>(new Set())
  const [resolveTarget, setResolveTarget] = useState<ReconciliationResult | null>(null)
  const [searchParams] = useSearchParams()

  const runsQuery = useReconRuns(orgId)
  const runQuery = useReconRun(orgId, selectedRunId)
  const resolveMutation = useResolveReconResult(orgId, selectedRunId)

  const statusFilter = searchParams.get('status') as ReconStatus | null
  const filteredResults = useMemo(() => {
    const all = runQuery.data?.results ?? []
    return statusFilter ? all.filter((r) => r.status === statusFilter) : all
  }, [runQuery.data, statusFilter])

  function toggleExpanded(id: string) {
    setExpanded((prev) => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }

  return (
    <div className="reconciliation-page">
      <h1>Reconciliation</h1>

      <RequireRole roles={['owner', 'ops_engineer', 'recon_analyst']}>
        <NewRunPanel orgId={orgId} onCreated={setSelectedRunId} />
      </RequireRole>

      <h2>Run history</h2>
      <div className="data-table-wrap" style={{ marginBottom: 'var(--sp-6)' }}>
        <table className="run-history-table data-table">
          <thead>
            <tr>
              <th>Created</th>
              <th>Total</th>
              <th>Matched</th>
              <th>Missing</th>
              <th>Duplicates</th>
              <th>Amount mismatches</th>
              <th>Unresolved</th>
            </tr>
          </thead>
          <tbody>
            {(runsQuery.data ?? []).map((run) => (
              <tr
                key={run.run_id}
                className={run.run_id === selectedRunId ? 'run-history-table__row--selected' : undefined}
                onClick={() => setSelectedRunId(run.run_id)}
                style={{ cursor: 'pointer' }}
              >
                <td style={{ fontFamily: 'var(--font-mono)' }}>{new Date(run.created_at).toLocaleString()}</td>
                <td>{run.total_records}</td>
                <td style={{ color: 'var(--color-success)', fontWeight: 600 }}>{run.matched}</td>
                <td style={{ color: run.missing > 0 ? 'var(--color-warning)' : 'inherit' }}>{run.missing}</td>
                <td style={{ color: run.duplicates > 0 ? 'var(--color-warning)' : 'inherit' }}>{run.duplicates}</td>
                <td style={{ color: run.amount_mismatches > 0 ? 'var(--color-critical)' : 'inherit' }}>{run.amount_mismatches}</td>
                <td style={{ color: run.unresolved > 0 ? 'var(--color-critical)' : 'inherit', fontWeight: run.unresolved > 0 ? 600 : 400 }}>{run.unresolved}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {selectedRunId && (
        <section className="run-detail">
          <h2>Run results</h2>
          <FilterBar fields={[{ key: 'status', label: 'Status', type: 'select', options: STATUS_OPTIONS }]} />

          <div className="data-table-wrap">
            <table className="run-detail-table data-table">
              <thead>
                <tr>
                  <th style={{ width: 32 }} />
                  <th>Ref</th>
                  <th>Status</th>
                  <th>Internal</th>
                  <th>Gateway</th>
                  <th>Bank</th>
                  <th>Resolved</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {filteredResults.map((result) => (
                  <Fragment key={result.result_id}>
                    <tr>
                      <td>
                        <button
                          type="button"
                          className="ghost"
                          style={{ padding: '2px 6px', fontSize: '0.75rem' }}
                          onClick={() => toggleExpanded(result.result_id)}
                          aria-label="Expand"
                        >
                          {expanded.has(result.result_id) ? '▾' : '▸'}
                        </button>
                      </td>
                      <td style={{ fontFamily: 'var(--font-mono)', fontWeight: 500 }}>{result.transaction_ref}</td>
                      <td>
                        <ReconStatusBadge status={result.status} />
                      </td>
                      <td style={{ fontFamily: 'var(--font-mono)' }}>{result.internal_amount ?? '—'}</td>
                      <td style={{ fontFamily: 'var(--font-mono)' }}>{result.gateway_amount ?? '—'}</td>
                      <td style={{ fontFamily: 'var(--font-mono)' }}>{result.bank_amount ?? '—'}</td>
                      <td>
                        <span style={{ color: result.resolved ? 'var(--color-success)' : 'var(--text-muted)' }}>
                          {result.resolved ? '✓ Yes' : 'No'}
                        </span>
                      </td>
                      <td>
                        {!result.resolved && result.status !== 'matched' && (
                          <RequireRole roles={['owner', 'recon_analyst']} mode="disable" disabledReason="Only an owner or recon analyst can resolve a mismatch">
                            <button
                              type="button"
                              className="secondary"
                              style={{ padding: '3px 10px', fontSize: '0.75rem', borderColor: 'var(--accent-primary)', color: 'var(--accent-primary-h)' }}
                              onClick={() => setResolveTarget(result)}
                            >
                              Resolve
                            </button>
                          </RequireRole>
                        )}
                      </td>
                    </tr>
                    {expanded.has(result.result_id) && (
                      <tr className="run-detail-table__expanded">
                        <td />
                        <td colSpan={7} style={{ background: 'rgba(15, 23, 42, 0.4)', padding: 'var(--sp-4)' }}>
                          <p style={{ marginBottom: 'var(--sp-2)' }}>
                            <strong>Probable cause:</strong> {result.probable_cause ?? 'n/a'}
                          </p>
                          {result.cause_confidence != null && (
                            <div style={{ marginBottom: 'var(--sp-2)' }}>
                              <ConfidenceBadge value={result.cause_confidence} label="Cause confidence" />
                            </div>
                          )}
                          {result.evidence.length > 0 && (
                            <ul style={{ paddingLeft: 'var(--sp-4)', margin: 'var(--sp-2) 0', color: 'var(--text-muted)', fontSize: '0.8125rem' }}>
                              {result.evidence.map((e, i) => (
                                <li key={i}>{e}</li>
                              ))}
                            </ul>
                          )}
                          {result.resolution_note && (
                            <p style={{ marginTop: 'var(--sp-2)', color: 'var(--color-success)', fontSize: '0.8125rem' }}>
                              <strong>Resolution note:</strong> {result.resolution_note}
                            </p>
                          )}
                        </td>
                      </tr>
                    )}
                  </Fragment>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {resolveTarget && (
        <ResolveModal
          transactionRef={resolveTarget.transaction_ref}
          isSubmitting={resolveMutation.isPending}
          onCancel={() => setResolveTarget(null)}
          onSubmit={(note) => {
            resolveMutation.mutate(
              { resultId: resolveTarget.result_id, note },
              { onSettled: () => setResolveTarget(null) },
            )
          }}
        />
      )}
    </div>
  )
}
