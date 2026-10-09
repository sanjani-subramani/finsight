import { useState } from 'react'
import './ConfirmDialog.css'

export interface ConfirmDialogProps {
  title: string
  message: string
  isSubmitting: boolean
  onCancel: () => void
  onConfirm: () => Promise<void>
}

/**
 * A compliance decision must be PESSIMISTIC, the opposite of
 * Reconciliation's resolve action: confirming a rule immediately makes
 * it eligible for run_impact_analysis (Step 17's hard human-review
 * gate), so nothing here shows a success state until the server has
 * actually responded. The dialog stays open with a disabled, "Confirming…"
 * button for the whole round trip; it only closes once onConfirm's
 * promise settles, whether that's success or failure.
 */
export function ConfirmDialog({ title, message, isSubmitting = false, onCancel, onConfirm }: ConfirmDialogProps) {
  const [error, setError] = useState<string | null>(null)
  // Tracked locally rather than trusting only the caller's isSubmitting
  // prop to be perfectly in sync with this exact call -- the dialog's own
  // in-flight state must reflect the promise IT is directly awaiting, so
  // "Confirming…" is guaranteed to show for the full round trip
  // regardless of how the parent wires its own pending state.
  const [isConfirming, setIsConfirming] = useState(false)
  const busy = isSubmitting || isConfirming

  async function handleConfirm() {
    setError(null)
    setIsConfirming(true)
    try {
      await onConfirm()
    } catch {
      setError('The server rejected this action. Nothing was confirmed.')
    } finally {
      setIsConfirming(false)
    }
  }

  return (
    <div className="confirm-dialog__backdrop" onClick={busy ? undefined : onCancel}>
      <div className="confirm-dialog" onClick={(e) => e.stopPropagation()} role="dialog" aria-label={title}>
        <h3>{title}</h3>
        <p>{message}</p>
        {error && <p className="confirm-dialog__error">{error}</p>}
        <div className="confirm-dialog__actions">
          <button type="button" onClick={onCancel} disabled={busy}>
            Cancel
          </button>
          <button type="button" onClick={handleConfirm} disabled={busy}>
            {busy ? 'Confirming…' : 'Yes, confirm'}
          </button>
        </div>
      </div>
    </div>
  )
}
