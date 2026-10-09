import { useState, type FormEvent } from 'react'
import { useThreatList, useThreatDetail, useAnalyzeSms, useAnalyzeUrl } from '../hooks/useThreat'
import type { ThreatEvent, ThreatEventSummary } from '../types/threat'

const CHANNEL_LABELS: Record<string, string> = {
  sms: '📱 SMS',
  url: '🔗 URL',
  qr_code: '📸 QR Code',
  voice_call: '📞 Voice',
}

const RISK_COLORS: Record<string, string> = {
  critical: 'var(--color-critical)',
  high: '#f97316',
  medium: 'var(--color-warning)',
  low: 'var(--color-info)',
  none: 'var(--color-success)',
}

function RiskGauge({ score }: { score: number }) {
  const pct = Math.round(score * 100)
  const circumference = 2 * Math.PI * 38
  const offset = circumference - (score * circumference)
  const color = score >= 0.8 ? RISK_COLORS.critical
    : score >= 0.6 ? RISK_COLORS.high
    : score >= 0.4 ? RISK_COLORS.medium
    : score >= 0.2 ? RISK_COLORS.low
    : RISK_COLORS.none

  return (
    <div style={{ position: 'relative', width: 90, height: 90 }}>
      <svg viewBox="0 0 80 80" width="90" height="90">
        <circle cx="40" cy="40" r="38" fill="none" stroke="var(--border-default)" strokeWidth="4" />
        <circle
          cx="40" cy="40" r="38" fill="none"
          stroke={color} strokeWidth="4" strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          style={{ transform: 'rotate(-90deg)', transformOrigin: '50% 50%', transition: 'stroke-dashoffset 0.8s ease-out' }}
        />
      </svg>
      <div style={{
        position: 'absolute', inset: 0,
        display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
      }}>
        <span style={{ fontFamily: 'var(--font-mono)', fontSize: '1.25rem', fontWeight: 700, color }}>{pct}%</span>
        <span style={{ fontSize: '0.6rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Risk</span>
      </div>
    </div>
  )
}

function getSeverityFromWeight(weight: number): ThreatSeverity {
  if (weight >= 35) return 'critical'
  if (weight >= 20) return 'high'
  if (weight >= 10) return 'medium'
  return 'low'
}

function getRecommendedAction(threat: ThreatEvent): string {
  if (threat.recommended_action) return threat.recommended_action
  if (threat.risk_score >= 0.7) {
    return 'Critical risk: Immediately block suspicious sender, blacklist domain at firewall, and alert impacted users.'
  }
  if (threat.risk_score >= 0.35) {
    return 'Suspicious activity: Advise recipient not to click links or provide credentials. Block sender and monitor account.'
  }
  return 'Low risk: Standard monitoring advised.'
}

function getExplanation(threat: ThreatEvent): string {
  if (threat.human_explanation) return threat.human_explanation
  const cat = threat.primary_category ? threat.primary_category.replace(/_/g, ' ') : 'phishing / scam'
  return `Identified ${cat} pattern across ${threat.signals.length} threat signal(s). The message contains deceptive indicators designed to manipulate the recipient.`
}

function ThreatDetailPanel({ threat }: { threat: ThreatEvent }) {
  const explanation = getExplanation(threat)
  const recommendation = getRecommendedAction(threat)

  return (
    <div className="glass-card animate-fade-in" style={{ marginTop: 'var(--sp-4)' }}>
      <div style={{ display: 'flex', gap: 'var(--sp-6)', alignItems: 'flex-start', flexWrap: 'wrap' }}>
        <RiskGauge score={threat.risk_score} />
        <div style={{ flex: 1, minWidth: 250 }}>
          <h3 style={{ marginBottom: 'var(--sp-2)' }}>{CHANNEL_LABELS[threat.channel] ?? threat.channel} Analysis</h3>
          <p style={{ fontSize: '0.875rem', lineHeight: 1.7 }}>{explanation}</p>
          <div style={{
            marginTop: 'var(--sp-3)', padding: 'var(--sp-3) var(--sp-4)',
            background: 'rgba(99, 102, 241, 0.08)', borderRadius: 'var(--radius-md)',
            fontSize: '0.8125rem', color: 'var(--accent-primary-h)',
          }}>
            <strong>Recommended:</strong> {recommendation}
          </div>
        </div>
      </div>

      {threat.signals.length > 0 && (
        <div style={{ marginTop: 'var(--sp-5)' }}>
          <h4>Detected Signals</h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--sp-2)', marginTop: 'var(--sp-2)' }}>
            {threat.signals.map((s, i) => {
              const signalName = s.name || s.signal_type || s.category || 'Threat Signal'
              const detailText = s.evidence || s.detail || `${s.detector ? s.detector.toUpperCase() : 'Engine'} detected ${s.category} (weight: ${s.weight})`
              const severity = s.severity || getSeverityFromWeight(s.weight ?? 15)

              return (
                <div key={i} style={{
                  display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                  padding: 'var(--sp-2) var(--sp-3)', borderRadius: 'var(--radius-sm)',
                  background: 'var(--bg-card)', fontSize: '0.8125rem',
                }}>
                  <span style={{ color: 'var(--text-secondary)' }}>
                    <strong style={{ color: 'var(--text-primary)' }}>{signalName.replace(/_/g, ' ')}:</strong> {detailText}
                  </span>
                  <span style={{
                    padding: '1px 8px', borderRadius: 'var(--radius-full)',
                    background: `color-mix(in srgb, ${RISK_COLORS[severity] ?? 'var(--text-muted)'} 15%, transparent)`,
                    color: RISK_COLORS[severity] ?? 'var(--text-muted)',
                    fontSize: '0.625rem', fontWeight: 600, textTransform: 'uppercase',
                  }}>{severity}</span>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {threat.impact && (
        <div style={{ marginTop: 'var(--sp-5)' }}>
          <h4>Financial Impact Assessment</h4>
          <div style={{
            marginTop: 'var(--sp-2)', padding: 'var(--sp-4)',
            background: threat.impact.would_cause_shortfall ? 'var(--color-critical-dim)' : 'var(--color-success-dim)',
            borderRadius: 'var(--radius-md)', fontSize: '0.875rem',
            color: threat.impact.would_cause_shortfall ? '#fca5a5' : 'var(--color-success)',
          }}>
            <p style={{ color: 'inherit' }}>{threat.impact.human_statement}</p>
            {threat.impact.obligations_at_risk.length > 0 && (
              <ul style={{ marginTop: 'var(--sp-2)', paddingLeft: 'var(--sp-5)' }}>
                {threat.impact.obligations_at_risk.map((o, i) => <li key={i}>{o}</li>)}
              </ul>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

function SubmitPanel({ onResult }: { onResult: (t: ThreatEvent) => void }) {
  const [mode, setMode] = useState<'sms' | 'url'>('sms')
  const [input, setInput] = useState('')
  const analyzeSms = useAnalyzeSms()
  const analyzeUrl = useAnalyzeUrl()

  const isPending = analyzeSms.isPending || analyzeUrl.isPending

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    if (!input.trim()) return
    const result = mode === 'sms'
      ? await analyzeSms.mutateAsync(input)
      : await analyzeUrl.mutateAsync(input)
    onResult(result)
    setInput('')
  }

  return (
    <div className="glass-card">
      <h2 style={{ margin: '0 0 var(--sp-4)' }}>Analyze Threat</h2>
      <div style={{ display: 'flex', gap: 'var(--sp-2)', marginBottom: 'var(--sp-4)' }}>
        {(['sms', 'url'] as const).map((m) => (
          <button
            key={m}
            type="button"
            className={mode === m ? '' : 'secondary'}
            onClick={() => setMode(m)}
            style={{ fontSize: '0.75rem', padding: 'var(--sp-1) var(--sp-4)' }}
          >
            {m === 'sms' ? '📱 SMS' : '🔗 URL'}
          </button>
        ))}
      </div>
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--sp-3)' }}>
        {mode === 'sms' ? (
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Paste a suspicious SMS message..."
            rows={4}
            required
          />
        ) : (
          <input
            type="url"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Enter a suspicious URL..."
            required
          />
        )}
        <button type="submit" disabled={isPending}>
          {isPending ? 'Analyzing…' : 'Analyze'}
        </button>
      </form>
    </div>
  )
}

export function ThreatIntelligence() {
  const threatsQuery = useThreatList()
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [latestResult, setLatestResult] = useState<ThreatEvent | null>(null)
  const detailQuery = useThreatDetail(selectedId)

  const displayedThreat = selectedId ? detailQuery.data : latestResult

  return (
    <div className="threat-page">
      <h1>Threat Intelligence</h1>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 360px', gap: 'var(--sp-6)' }}>
        <div>
          {displayedThreat && <ThreatDetailPanel threat={displayedThreat} />}

          <h2>Recent Threats</h2>
          {threatsQuery.isLoading && <p>Loading…</p>}
          {threatsQuery.data?.length === 0 && <p style={{ color: 'var(--text-muted)' }}>No threats detected yet.</p>}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--sp-2)' }}>
            {(threatsQuery.data ?? []).map((t: ThreatEventSummary) => {
              const tid = t.id || t.threat_id || ''
              const dateStr = t.detected_at || t.created_at
              const dateDisplay = dateStr ? new Date(dateStr).toLocaleString() : '—'
              const riskLabel = t.risk_label || t.primary_category?.replace(/_/g, ' ') || (t.risk_score >= 0.6 ? 'high' : t.risk_score >= 0.3 ? 'medium' : 'low')
              const summaryText = t.raw_input_summary || (t.primary_category ? t.primary_category.replace(/_/g, ' ') : 'Threat Event')

              return (
                <div
                  key={tid}
                  onClick={() => { setSelectedId(tid); setLatestResult(null) }}
                  style={{
                    display: 'flex', alignItems: 'center', gap: 'var(--sp-4)',
                    padding: 'var(--sp-3) var(--sp-4)', borderRadius: 'var(--radius-md)',
                    background: selectedId === tid ? 'rgba(99, 102, 241, 0.1)' : 'var(--bg-card)',
                    border: `1px solid ${selectedId === tid ? 'rgba(99, 102, 241, 0.3)' : 'var(--border-subtle)'}`,
                    cursor: 'pointer', transition: 'all var(--transition-fast)',
                  }}
                >
                  <span style={{ fontSize: '1.2rem' }}>{CHANNEL_LABELS[t.channel]?.substring(0, 2) ?? '⚠️'}</span>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ fontSize: '0.8125rem', color: 'var(--text-primary)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', textTransform: 'capitalize' }}>
                      {summaryText}
                    </div>
                    <div style={{ fontSize: '0.6875rem', color: 'var(--text-muted)' }}>
                      {dateDisplay}
                    </div>
                  </div>
                  <span style={{
                    padding: '2px 8px', borderRadius: 'var(--radius-full)',
                    fontSize: '0.625rem', fontWeight: 700, textTransform: 'uppercase',
                    background: `color-mix(in srgb, ${RISK_COLORS[riskLabel] ?? 'var(--text-muted)'} 15%, transparent)`,
                    color: RISK_COLORS[riskLabel] ?? 'var(--text-muted)',
                  }}>{riskLabel}</span>
                </div>
              )
            })}
          </div>
        </div>

        <aside>
          <SubmitPanel onResult={(t) => { setLatestResult(t); setSelectedId(null) }} />
        </aside>
      </div>
    </div>
  )
}
