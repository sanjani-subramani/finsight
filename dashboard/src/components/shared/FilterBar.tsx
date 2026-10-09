import { useSearchParams } from 'react-router-dom'
import './FilterBar.css'

export interface FilterField {
  key: string
  label: string
  type: 'text' | 'select' | 'date'
  options?: { value: string; label: string }[]
}

export interface FilterBarProps {
  fields: FilterField[]
}

/**
 * Reusable filter row whose state syncs to the URL query string via
 * useSearchParams -- a filtered view (e.g. "PayTrace transactions,
 * status=bank_failed, provider=razorpay") is then just a URL, shareable
 * by link and restored correctly on reload, rather than living only in
 * component state that resets the moment the page is left.
 */
export function FilterBar({ fields }: FilterBarProps) {
  const [searchParams, setSearchParams] = useSearchParams()

  function handleChange(key: string, value: string) {
    const next = new URLSearchParams(searchParams)
    if (value) next.set(key, value)
    else next.delete(key)
    setSearchParams(next)
  }

  return (
    <div className="filter-bar">
      {fields.map((field) => {
        const value = searchParams.get(field.key) ?? ''
        if (field.type === 'select') {
          return (
            <label key={field.key} className="filter-bar__field">
              <span>{field.label}</span>
              <select
                aria-label={field.label}
                value={value}
                onChange={(e) => handleChange(field.key, e.target.value)}
              >
                <option value="">All</option>
                {field.options?.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </label>
          )
        }
        return (
          <label key={field.key} className="filter-bar__field">
            <span>{field.label}</span>
            <input
              aria-label={field.label}
              type={field.type === 'date' ? 'date' : 'text'}
              value={value}
              onChange={(e) => handleChange(field.key, e.target.value)}
            />
          </label>
        )
      })}
      {fields.some((f) => (searchParams.get(f.key) ?? '') !== '') && (
        <button type="button" className="filter-bar__clear" onClick={() => setSearchParams(new URLSearchParams())}>
          Clear filters
        </button>
      )}
    </div>
  )
}
