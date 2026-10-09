import { useState, type FormEvent } from 'react'
import { RequireRole } from '../auth/RequireRole'
import { useOrgAuth } from '../auth/useOrgAuth'
import { RuleCard } from '../components/compliance/RuleCard'
import { GraphView } from '../components/dependencies/GraphView'
import { useCriticalNodes, useGraph } from '../hooks/useFingraph'
import {
  useAnalyzeRule,
  useConfirmedRules,
  useIngestRegulation,
  usePendingRules,
  useReviewRule,
} from '../hooks/useRegimpact'
import type { ImpactReport } from '../types/regimpact'

function IngestRegulationForm({ orgId, onIngested }: { orgId: string; onIngested: () => void }) {
  const ingest = useIngestRegulation(orgId)
  const [title, setTitle] = useState('')
  const [sourceText, setSourceText] = useState('')
  const [sourceUrl, setSourceUrl] = useState('')
  const [effectiveDate, setEffectiveDate] = useState('')

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    await ingest.mutateAsync({
      title,
      source_text: sourceText,
      source_url: sourceUrl || null,
      effective_date: effectiveDate || null,
    })
    setTitle('')
    setSourceText('')
    setSourceUrl('')
    setEffectiveDate('')
    onIngested()
  }

  return (
    <form className="ingest-regulation-form" onSubmit={handleSubmit}>
      <h2>Ingest regulation</h2>
      <label>
        Title
        <input value={title} onChange={(e) => setTitle(e.target.value)} required />
      </label>
      <label>
        Source text
        <textarea value={sourceText} onChange={(e) => setSourceText(e.target.value)} rows={6} required />
      </label>
      <label>
        Source URL
        <input value={sourceUrl} onChange={(e) => setSourceUrl(e.target.value)} />
      </label>
      <label>
        Effective date
        <input type="date" value={effectiveDate} onChange={(e) => setEffectiveDate(e.target.value)} />
      </label>
      <button type="submit" disabled={ingest.isPending}>
        {ingest.isPending ? 'Extracting rules…' : 'Ingest and extract'}
      </button>
      {ingest.isError && <p className="ingest-regulation-form__error">Could not ingest this regulation.</p>}
    </form>
  )
}

function ImpactReportView({ report, orgId }: { report: ImpactReport; orgId: string }) {
  const graphQuery = useGraph(orgId)
  const centralityQuery = useCriticalNodes(orgId)
  const highlighted = new Set(report.affected_service_nodes)

  return (
    <div className="impact-report-view">
      <h4>Impact report</h4>
      <p>{report.estimated_transactions.toLocaleString()} estimated transactions affected</p>

      <h5>Affected products</h5>
      <ul>{report.affected_products.map((p) => <li key={p}>{p}</li>)}</ul>
      <h5>Affected workflows</h5>
      <ul>{report.affected_workflows.map((w) => <li key={w}>{w}</li>)}</ul>
      <h5>Affected service nodes</h5>
      <ul>{report.affected_service_nodes.map((s) => <li key={s}>{s}</li>)}</ul>
      <h5>Required changes</h5>
      <ul>{report.required_changes.map((c, i) => <li key={i}>{c}</li>)}</ul>

      {/* Reusing GraphView from the Dependencies page (Step 18/9) with the
          same highlighted-node mechanism as a failure simulation --
          this visually proves the RegImpact-FinGraph reuse from Step 17:
          the exact same graph primitives and the exact same "highlight
          only what the backend returned" rule apply whether the trigger
          was a simulated outage or a confirmed regulatory rule. */}
      {graphQuery.data && (
        <GraphView graph={graphQuery.data} centrality={centralityQuery.data ?? []} highlightedNodes={highlighted} height={320} />
      )}
    </div>
  )
}

export function Compliance() {
  const { currentOrgId } = useOrgAuth()
  const orgId = currentOrgId as string
  const pendingQuery = usePendingRules(orgId)
  const confirmedQuery = useConfirmedRules(orgId)
  const reviewRule = useReviewRule(orgId)
  const analyzeRule = useAnalyzeRule(orgId)
  const [reports, setReports] = useState<Record<string, ImpactReport>>({})
  const [analyzeError, setAnalyzeError] = useState<Record<string, string>>({})

  async function handleAnalyze(ruleId: string) {
    setAnalyzeError((prev) => ({ ...prev, [ruleId]: '' }))
    try {
      const report = await analyzeRule.mutateAsync(ruleId)
      setReports((prev) => ({ ...prev, [ruleId]: report }))
    } catch {
      setAnalyzeError((prev) => ({ ...prev, [ruleId]: 'Impact analysis failed.' }))
    }
  }

  return (
    <div className="compliance-page">
      <h1>Compliance</h1>

      <RequireRole roles={['owner', 'ops_engineer']}>
        <IngestRegulationForm orgId={orgId} onIngested={() => pendingQuery.refetch()} />
      </RequireRole>

      <h2>Review queue</h2>
      {pendingQuery.data?.length === 0 && <p>No rules pending review.</p>}
      {(pendingQuery.data ?? []).map((rule) => (
        <RuleCard
          key={rule.id}
          rule={rule}
          isSubmitting={reviewRule.isPending && reviewRule.variables?.ruleId === rule.id}
          onReview={async (decision, note) => {
            await reviewRule.mutateAsync({ ruleId: rule.id, decision, note })
          }}
        />
      ))}

      <h2>Confirmed rules</h2>
      {confirmedQuery.data?.length === 0 && <p>No confirmed rules yet.</p>}
      {(confirmedQuery.data ?? []).map((rule) => (
        <div key={rule.id} className="confirmed-rule-card">
          <p className="confirmed-rule-card__summary">{rule.rule_text}</p>
          <button type="button" onClick={() => handleAnalyze(rule.id)} disabled={analyzeRule.isPending}>
            {analyzeRule.isPending ? 'Analyzing…' : 'Analyze impact'}
          </button>
          {analyzeError[rule.id] && <p className="ingest-regulation-form__error">{analyzeError[rule.id]}</p>}
          {reports[rule.id] && <ImpactReportView report={reports[rule.id]} orgId={orgId} />}
        </div>
      ))}
    </div>
  )
}
