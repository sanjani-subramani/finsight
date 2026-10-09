import { useState } from 'react'
import './ResolveModal.css'

export interface ResolveModalProps {
  transactionRef: string
  onCancel: () => void
  onSubmit: (note: string) => void
  isSubmitting?: boolean
}

export function ResolveModal({ transactionRef, onCancel, onSubmit, isSubmitting }: ResolveModalProps) {
  const [note, setNote] = useState('')

  return (
    <div className="resolve-modal__backdrop" onClick={onCancel}>
      <div className="resolve-modal" onClick={(e) => e.stopPropagation()} role="dialog" aria-label="Resolve mismatch">
        <h3>Resolve {transactionRef}</h3>
        <label>
          Resolution note
          <textarea value={note} onChange={(e) => setNote(e.target.value)} rows={4} />
        </label>
        <div className="resolve-modal__actions">
          <button type="button" onClick={onCancel}>
            Cancel
          </button>
          <button type="button" disabled={!note.trim() || isSubmitting} onClick={() => onSubmit(note.trim())}>
            {isSubmitting ? 'Saving…' : 'Resolve'}
          </button>
        </div>
      </div>
    </div>
  )
}
