import { describe, expect, it } from 'vitest'
import { buildHighlightedNodeSet } from './highlight'
import type { ImpactResult } from '../../types/fingraph'

describe('buildHighlightedNodeSet', () => {
  it('highlights exactly the nodes returned by the backend, nothing more', () => {
    const impact: ImpactResult = {
      impact_id: 'impact-1',
      failed_node: 'KYC Provider',
      affected_services: [],
      affected_workflows: ['Onboarding', 'Loans', 'Cards'],
      estimated_transactions: 18420,
      critical_paths: [['Loans', 'Onboarding', 'KYC Provider']],
      alternative_providers: [],
    }

    const highlighted = buildHighlightedNodeSet(impact)

    expect(highlighted).toEqual(new Set(['KYC Provider', 'Onboarding', 'Loans', 'Cards']))
    // A node that exists in the wider graph but was NOT returned by the
    // backend (e.g. an unrelated service) must never end up highlighted --
    // that would be exactly the "client-side approximation" this function
    // exists to rule out.
    expect(highlighted.has('Unrelated Service')).toBe(false)
  })

  it('an empty blast radius highlights only the failed node itself', () => {
    const impact: ImpactResult = {
      impact_id: 'impact-2',
      failed_node: 'Leaf Service',
      affected_services: [],
      affected_workflows: [],
      estimated_transactions: 0,
      critical_paths: [],
      alternative_providers: [],
    }

    expect(buildHighlightedNodeSet(impact)).toEqual(new Set(['Leaf Service']))
  })
})
