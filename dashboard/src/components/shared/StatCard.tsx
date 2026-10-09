import { Link } from 'react-router-dom'
import './StatCard.css'

type Severity = 'ok' | 'warning' | 'critical'

interface StatCardProps {
  label: string
  value: string | number
  severity?: Severity
  detail?: string
  href?: string
}

export function StatCard({ label, value, severity, detail, href }: StatCardProps) {
  const className = `stat-card${severity ? ` stat-card--${severity}` : ''}`

  const content = (
    <>
      <div className="stat-card__label">
        {severity && <span className={`stat-card__dot stat-card__dot--${severity}`} />}
        {label}
      </div>
      <div className="stat-card__value">{value}</div>
      {detail && <div className="stat-card__detail">{detail}</div>}
    </>
  )

  if (href) {
    return (
      <Link to={href} className={className}>
        {content}
      </Link>
    )
  }

  return <div className={className}>{content}</div>
}
