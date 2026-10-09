import type { ProviderAlert } from '../../types/paytrace'
import './ProviderAlertBanner.css'

// Rendered visually URGENT (red, not a subtle toast) -- a provider
// degradation alert is exactly the kind of thing an ops dashboard exists
// to surface loudly; burying it as a quiet badge would defeat the point
// of Step 16's early-warning detector.
export function ProviderAlertBanner({ alert }: { alert: ProviderAlert }) {
  return (
    <div className="provider-alert-banner" role="alert">
      <span className="provider-alert-banner__icon" aria-hidden="true">
        ⚠
      </span>
      <span>{alert.message}</span>
    </div>
  )
}
