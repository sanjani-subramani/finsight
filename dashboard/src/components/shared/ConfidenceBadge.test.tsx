import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { ConfidenceBadge } from './ConfidenceBadge'

describe('ConfidenceBadge', () => {
  it('renders the high tier at 0.9 -- solid, no warning icon', () => {
    render(<ConfidenceBadge value={0.9} />)
    const badge = screen.getByTestId('confidence-badge')
    expect(badge.dataset.tier).toBe('high')
    expect(badge).toHaveTextContent('90%')
    expect(badge).not.toHaveTextContent('⚠')
  })

  it('renders the medium tier at 0.6 -- distinct from high, no warning icon', () => {
    render(<ConfidenceBadge value={0.6} />)
    const badge = screen.getByTestId('confidence-badge')
    expect(badge.dataset.tier).toBe('medium')
    expect(badge).toHaveTextContent('60%')
    expect(badge).not.toHaveTextContent('⚠')
  })

  it('renders the low tier at 0.3 -- prominent warning icon', () => {
    render(<ConfidenceBadge value={0.3} />)
    const badge = screen.getByTestId('confidence-badge')
    expect(badge.dataset.tier).toBe('low')
    expect(badge).toHaveTextContent('30%')
    expect(badge).toHaveTextContent('⚠')
  })

  it('all three tiers are visually distinct from one another', () => {
    const { unmount: u1 } = render(<ConfidenceBadge value={0.9} />)
    const high = screen.getByTestId('confidence-badge').className
    u1()
    const { unmount: u2 } = render(<ConfidenceBadge value={0.6} />)
    const medium = screen.getByTestId('confidence-badge').className
    u2()
    render(<ConfidenceBadge value={0.3} />)
    const low = screen.getByTestId('confidence-badge').className

    expect(new Set([high, medium, low]).size).toBe(3)
  })
})
