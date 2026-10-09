import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { OrgAuthContext, type OrgAuthContextValue } from '../../auth/OrgAuthContext'
import { RuleCard } from './RuleCard'
import type { RegulatoryRule } from '../../types/regimpact'

function withOwnerRole(children: React.ReactNode) {
  const value: OrgAuthContextValue = {
    user: null,
    orgs: [],
    currentOrgId: 'org-1',
    currentMembership: { org_id: 'org-1', org_name: 'Acme', org_slug: 'acme', role: 'owner' },
    currentRole: 'owner',
    isAuthenticated: true,
    isLoading: false,
    login: async () => {},
    logout: () => {},
    switchOrg: () => {},
  }
  return <OrgAuthContext.Provider value={value}>{children}</OrgAuthContext.Provider>
}

function makeRule(overrides: Partial<RegulatoryRule>): RegulatoryRule {
  return {
    id: 'rule-1',
    regulation_id: 'reg-1',
    rule_text: 'Report suspicious transactions within 3 days.',
    trigger_condition: 'A transaction exceeds the threshold.',
    threshold_json: null,
    required_action: 'File a report',
    deadline_days: 3,
    applies_to_product_categories: ['savings_account'],
    extraction_confidence: 0.9,
    ambiguities: [],
    status: 'pending_review',
    reviewed_by: null,
    reviewed_at: null,
    review_note: null,
    ...overrides,
  }
}

describe('RuleCard -- confidence-driven trust cues', () => {
  it('a high-confidence rule with no ambiguities looks clean', () => {
    render(withOwnerRole(<RuleCard rule={makeRule({})} onReview={vi.fn()} isSubmitting={false} />))
    const card = screen.getByTestId('rule-card')
    expect(card.dataset.needsCaution).toBe('false')
    expect(screen.queryByTestId('ambiguities')).not.toBeInTheDocument()
  })

  it('a low-confidence rule with ambiguities looks visibly less trustworthy', () => {
    render(
      withOwnerRole(
        <RuleCard
          rule={makeRule({ extraction_confidence: 0.3, ambiguities: ['Unclear which accounts this covers'] })}
          onReview={vi.fn()}
          isSubmitting={false}
        />,
      ),
    )
    const card = screen.getByTestId('rule-card')
    expect(card.dataset.needsCaution).toBe('true')
    expect(screen.getByTestId('ambiguities')).toBeInTheDocument()
    expect(screen.getByTestId('ambiguities')).toHaveTextContent('Unclear which accounts this covers')
  })

  it('the clean and cautioned cards render with different classes', () => {
    const { unmount } = render(withOwnerRole(<RuleCard rule={makeRule({})} onReview={vi.fn()} isSubmitting={false} />))
    const cleanClass = screen.getByTestId('rule-card').className
    unmount()

    render(
      withOwnerRole(
        <RuleCard
          rule={makeRule({ extraction_confidence: 0.3, ambiguities: ['doubt'] })}
          onReview={vi.fn()}
          isSubmitting={false}
        />,
      ),
    )
    const cautionClass = screen.getByTestId('rule-card').className

    expect(cleanClass).not.toBe(cautionClass)
  })
})

describe('RuleCard -- confirm is pessimistic', () => {
  it('shows no success state until the mocked onReview promise resolves', async () => {
    const user = userEvent.setup()
    let resolveReview: (() => void) | undefined
    const onReview = vi.fn(
      () =>
        new Promise<void>((resolve) => {
          resolveReview = resolve
        }),
    )

    render(withOwnerRole(<RuleCard rule={makeRule({})} onReview={onReview} isSubmitting={false} />))

    await user.click(screen.getByText('Confirm'))
    await user.click(screen.getByText('Yes, confirm'))

    // While the mocked API call is still pending, the confirm dialog
    // must still be showing its in-flight state -- never a success
    // message, and never dismissed as if it had already worked.
    expect(screen.getByText('Confirming…')).toBeInTheDocument()
    expect(screen.queryByText(/confirmed/i, { selector: '.rule-card__summary' })).not.toBeInTheDocument()

    resolveReview?.()
    await screen.findByText('Confirm')
  })
})
