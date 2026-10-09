import { useMemo, useState } from 'react'
import { RequireRole } from '../auth/RequireRole'
import { useOrgAuth } from '../auth/useOrgAuth'
import { EdgeForm } from '../components/dependencies/EdgeForm'
import { GraphView } from '../components/dependencies/GraphView'
import { buildHighlightedNodeSet } from '../components/dependencies/highlight'
import { NodeForm } from '../components/dependencies/NodeForm'
import { useCriticalNodes, useGraph, useSimulateFailure } from '../hooks/useFingraph'
import type { ImpactResult } from '../types/fingraph'

export function Dependencies() {
  const { currentOrgId } = useOrgAuth()
  const orgId = currentOrgId as string
  const graphQuery = useGraph(orgId)
  const centralityQuery = useCriticalNodes(orgId)
  const simulate = useSimulateFailure(orgId)

  const [selectedNode, setSelectedNode] = useState<string | null>(null)
  const [impact, setImpact] = useState<ImpactResult | null>(null)

  const highlighted = useMemo(() => (impact ? buildHighlightedNodeSet(impact) : undefined), [impact])

  async function handleSimulate() {
    if (!selectedNode) return
    const result = await simulate.mutateAsync({ nodeName: selectedNode })
    setImpact(result)
  }

  if (graphQuery.isLoading || !graphQuery.data) {
    return <p>Loading graph…</p>
  }

  const cycleWarnings = graphQuery.data.cycle_warnings

  return (
    <div className="dependencies-page">
      <h1>Dependencies</h1>

      {cycleWarnings.length > 0 && (
        <div className="cycle-warning-banner" role="alert">
          <strong>Dependency cycle detected.</strong> A cycle is almost always a modelling error --
          the blast-radius algorithm gives unreliable answers until it's fixed.
          <ul>
            {cycleWarnings.map((w, i) => (
              <li key={i}>{w}</li>
            ))}
          </ul>
        </div>
      )}

      <div className="dependencies-layout">
        <div className="dependencies-graph">
          <GraphView
            graph={graphQuery.data}
            centrality={centralityQuery.data ?? []}
            highlightedNodes={highlighted}
            onNodeClick={setSelectedNode}
          />
        </div>

        <aside className="dependencies-sidebar">
          {selectedNode ? (
            <div className="node-detail">
              <h2>{selectedNode}</h2>
              {(() => {
                const node = graphQuery.data!.nodes.find((n) => n.name === selectedNode)
                if (!node) return null
                return (
                  <ul>
                    <li>Type: {node.node_type}</li>
                    <li>Critical: {node.is_critical ? 'Yes' : 'No'}</li>
                  </ul>
                )
              })()}

              <RequireRole roles={['owner', 'ops_engineer']} mode="disable">
                <button type="button" onClick={handleSimulate} disabled={simulate.isPending}>
                  {simulate.isPending ? 'Simulating…' : 'Simulate failure'}
                </button>
              </RequireRole>

              {impact && impact.failed_node === selectedNode && (
                <div className="impact-summary">
                  <h3>Blast radius</h3>
                  <p>{impact.estimated_transactions.toLocaleString()} estimated transactions affected</p>
                  <h4>Affected services</h4>
                  <ul>{impact.affected_services.map((s) => <li key={s}>{s}</li>)}</ul>
                  <h4>Affected workflows</h4>
                  <ul>{impact.affected_workflows.map((w) => <li key={w}>{w}</li>)}</ul>
                  {impact.critical_paths.length > 0 && (
                    <>
                      <h4>Critical paths</h4>
                      <ul>
                        {impact.critical_paths.map((path, i) => (
                          <li key={i}>{path.join(' → ')}</li>
                        ))}
                      </ul>
                    </>
                  )}
                  {impact.alternative_providers.length > 0 && (
                    <>
                      <h4>Alternative providers</h4>
                      <ul>{impact.alternative_providers.map((p) => <li key={p}>{p}</li>)}</ul>
                    </>
                  )}
                </div>
              )}
            </div>
          ) : (
            <p>Click a node to see details.</p>
          )}

          <RequireRole roles={['owner']}>
            <NodeForm orgId={orgId} />
            <EdgeForm orgId={orgId} nodes={graphQuery.data.nodes} />
          </RequireRole>
        </aside>
      </div>
    </div>
  )
}
