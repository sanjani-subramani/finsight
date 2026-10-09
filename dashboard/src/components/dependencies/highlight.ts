import type { ImpactResult } from '../../types/fingraph'

/**
 * The set of node names GraphView should highlight after a simulation --
 * built EXCLUSIVELY from the backend's ImpactResult (the failed node plus
 * affected_services and affected_workflows verbatim). This function must
 * never do its own graph traversal: FinGraph's blast-radius algorithm
 * (Step 16) is the single source of truth for "what does X failing
 * affect," and a client-side approximation here could silently drift
 * from it and show an ops engineer a blast radius that isn't the one the
 * backend actually computed.
 */
export function buildHighlightedNodeSet(impact: ImpactResult): Set<string> {
  return new Set<string>([impact.failed_node, ...impact.affected_services, ...impact.affected_workflows])
}
