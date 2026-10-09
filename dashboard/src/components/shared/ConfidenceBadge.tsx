import './ConfidenceBadge.css'

export type ConfidenceTier = 'high' | 'medium' | 'low'

export function confidenceTier(value: number): ConfidenceTier {
  if (value >= 0.75) return 'high'
  if (value >= 0.5) return 'medium'
  return 'low'
}

export interface ConfidenceBadgeProps {
  value: number
  label?: string
}

/**
 * Same visual-tiering concept as the Flutter app's ConfidenceIndicator
 * (Step 13), expressed for a desktop audience: >=0.75 renders as a plain,
 * solid badge (high confidence shouldn't call attention to itself);
 * 0.50-0.74 renders with a subtle warning styling; <0.50 renders with a
 * prominent warning icon and colour. This is the same honesty principle
 * throughout the product -- a number without a trustworthiness cue lets
 * someone act on data that might be wrong without ever knowing to
 * double-check it, whether that's a personal budget on a phone or a
 * compliance decision on this dashboard.
 */
export function ConfidenceBadge({ value, label }: ConfidenceBadgeProps) {
  const tier = confidenceTier(value)
  const pct = Math.round(value * 100)
  const radius = 11
  const circumference = 2 * Math.PI * radius
  const offset = circumference - value * circumference

  return (
    <span
      className={`confidence-badge confidence-badge--${tier}`}
      data-testid="confidence-badge"
      data-tier={tier}
      role="status"
    >
      <div className="confidence-badge__ring" aria-hidden="true">
        <svg viewBox="0 0 28 28">
          <circle cx="14" cy="14" r={radius} className="confidence-badge__ring-bg" />
          <circle
            cx="14"
            cy="14"
            r={radius}
            className={`confidence-badge__ring-fill confidence-badge__ring-fill--${tier}`}
            strokeDasharray={circumference}
            strokeDashoffset={offset}
          />
        </svg>
      </div>
      {label && <span className="confidence-badge__label">{label}:</span>}
      <span className={`confidence-badge__value confidence-badge__value--${tier}`}>
        {tier === 'low' && (
          <span className="confidence-badge__icon" aria-hidden="true" style={{ marginRight: 4 }}>
            ⚠
          </span>
        )}
        {pct}%
      </span>
    </span>
  )
}
