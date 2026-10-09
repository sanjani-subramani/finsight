import { useState } from 'react'
import { RequireRole } from '../../auth/RequireRole'
import type { RegulatoryRule } from '../../types/regimpact'
import { ConfidenceBadge, confidenceTier } from '../shared/ConfidenceBadge'
import { ConfirmDialog } from './ConfirmDialog'
import './RuleCard.css'

export interface RuleCardProps {
  rule: RegulatoryRule
  onReview: (decision: 'confirmed' | 'rejected', note?: string) => Promise<void>
  isSubmitting: boolean
}

/**
 * THE HONESTY SHOWCASE. A rule with low extraction confidence or any
 * listed ambiguities must visually look LESS trustworthy than a clean,
 * high-confidence one -- the same principle as the Flutter app's
 * confidence display (Step 13), applied here to a compliance decision
 * instead of a personal-finance one. This is deliberate: a compliance
 * officer skimming a review queue should never have to read every field
 * closely to notice "the model wasn't sure about this one."
 */
export function RuleCard({ rule, onReview, isSubmitting }: RuleCardProps) {
  const [showConfirm, setShowConfirm] = useState(false)
  const [showRejectForm, setShowRejectForm] = useState(false)
  const [rejectNote, setRejectNote] = useState('')

  const tier = rule.extraction_confidence != null ? confidenceTier(rule.extraction_confidence) : 'low'
  const needsCaution = tier !== 'high' || rule.ambiguities.length > 0

  return (
    <div
      className={`rule-card ${needsCaution ? 'rule-card--caution' : 'rule-card--clean'}`}
      data-testid="rule-card"
      data-needs-caution={needsCaution}
    >
      <p className="rule-card__summary">{rule.rule_text}</p>
      <dl className="rule-card__fields">
        <dt>Trigger</dt>
        <dd>{rule.trigger_condition}</dd>
        <dt>Required action</dt>
        <dd>{rule.required_action}</dd>
        <dt>Deadline</dt>
        <dd>{rule.deadline_days != null ? `${rule.deadline_days} days` : 'Not specified'}</dd>
      </dl>

      {rule.extraction_confidence != null && (
        <ConfidenceBadge value={rule.extraction_confidence} label="Extraction confidence" />
      )}

      {rule.ambiguities.length > 0 && (
        <div className="rule-card__ambiguities" role="alert" data-testid="ambiguities">
          <strong>⚠ Ambiguities flagged during extraction</strong>
          <ul>
            {rule.ambiguities.map((a, i) => (
              <li key={i}>{a}</li>
            ))}
          </ul>
        </div>
      )}

      <div className="rule-card__actions">
        <RequireRole roles={['owner', 'ops_engineer']} mode="disable">
          <button type="button" onClick={() => setShowConfirm(true)}>
            Confirm
          </button>
        </RequireRole>
        <RequireRole roles={['owner', 'ops_engineer']} mode="disable">
          <button type="button" onClick={() => setShowRejectForm(true)}>
            Reject
          </button>
        </RequireRole>
      </div>

      {showRejectForm && (
        <div className="rule-card__reject-form">
          <textarea
            value={rejectNote}
            onChange={(e) => setRejectNote(e.target.value)}
            placeholder="Reason for rejection (required)"
            rows={3}
          />
          <div className="rule-card__reject-actions">
            <button type="button" onClick={() => setShowRejectForm(false)} disabled={isSubmitting}>
              Cancel
            </button>
            <button
              type="button"
              disabled={!rejectNote.trim() || isSubmitting}
              onClick={async () => {
                await onReview('rejected', rejectNote.trim())
                setShowRejectForm(false)
              }}
            >
              {isSubmitting ? 'Rejecting…' : 'Confirm rejection'}
            </button>
          </div>
        </div>
      )}

      {showConfirm && (
        <ConfirmDialog
          title="Confirm this rule?"
          message="Confirming makes this rule eligible for impact analysis (Step 17's human-review gate). This is a compliance decision -- make sure you've read it, not just the confidence badge."
          isSubmitting={isSubmitting}
          onCancel={() => setShowConfirm(false)}
          onConfirm={async () => {
            await onReview('confirmed')
            setShowConfirm(false)
          }}
        />
      )}
    </div>
  )
}
