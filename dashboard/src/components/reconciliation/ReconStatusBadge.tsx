import type { ReconStatus } from '../../types/reconx'
import './ReconStatusBadge.css'

const STATUS_COLOR: Record<ReconStatus, string> = {
  matched: 'green',
  missing_in_bank: 'orange',
  missing_in_gateway: 'orange',
  missing_in_internal: 'orange',
  duplicate: 'red',
  amount_mismatch: 'red',
  timing_difference: 'blue',
  unresolved: 'grey',
}

export function ReconStatusBadge({ status }: { status: ReconStatus }) {
  return (
    <span className={`recon-status-badge recon-status-badge--${STATUS_COLOR[status]}`}>
      {status.replace(/_/g, ' ')}
    </span>
  )
}
