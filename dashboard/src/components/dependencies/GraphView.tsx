import ForceGraph2D from 'react-force-graph-2d'
import type { CentralityScore, GraphResponse } from '../../types/fingraph'

interface RenderNode {
  id: string
  node_type: string
  is_critical: boolean
}

export interface GraphViewProps {
  graph: GraphResponse
  centrality: CentralityScore[]
  /**
   * Exact node-name set to highlight, or undefined for "no simulation
   * active, show the whole graph normally." This must always come
   * straight from a backend ImpactResult's affected_services /
   * affected_workflows -- NEVER computed by walking the graph in the
   * browser. FinGraph's blast-radius algorithm (Step 16) is the single
   * source of truth for "what does X failing affect"; a client-side
   * approximation could silently drift from it and show an ops engineer
   * a blast radius that isn't the one the backend actually computed.
   */
  highlightedNodes?: Set<string>
  onNodeClick?: (nodeName: string) => void
  height?: number
}

export function GraphView({ graph, centrality, highlightedNodes, onNodeClick, height = 480 }: GraphViewProps) {
  const centralityByName = new Map(centrality.map((c) => [c.node_name, c.betweenness]))
  const maxBetweenness = Math.max(1e-6, ...centrality.map((c) => c.betweenness))
  const dimming = highlightedNodes !== undefined

  const graphData = {
    nodes: graph.nodes.map((n) => ({ id: n.name, node_type: n.node_type, is_critical: n.is_critical })),
    links: graph.edges.map((e) => ({ source: e.from_name, target: e.to_name })),
  }

  return (
    <ForceGraph2D
      graphData={graphData}
      height={height}
      backgroundColor="#0b0f1a"
      nodeLabel={(node) => `${(node as RenderNode).id} (${(node as RenderNode).node_type})`}
      linkDirectionalArrowLength={4}
      linkDirectionalArrowRelPos={1}
      linkDirectionalArrowColor={() => (dimming ? 'rgba(148, 163, 184, 0.15)' : 'rgba(99, 102, 241, 0.4)')}
      linkColor={() => (dimming ? 'rgba(148, 163, 184, 0.1)' : 'rgba(148, 163, 184, 0.25)')}
      onNodeClick={(node) => onNodeClick?.((node as RenderNode).id)}
      nodeCanvasObject={(nodeRaw, ctx, globalScale) => {
        const node = nodeRaw as RenderNode & { x?: number; y?: number }
        if (node.x == null || node.y == null) return

        const betweenness = centralityByName.get(node.id) ?? 0
        const radius = 5 + 15 * (betweenness / maxBetweenness)
        const isHighlighted = highlightedNodes?.has(node.id)
        const isDimmed = dimming && !isHighlighted

        ctx.beginPath()
        ctx.arc(node.x, node.y, radius, 0, 2 * Math.PI)

        if (isDimmed) {
          ctx.fillStyle = 'rgba(71, 85, 105, 0.3)'
          ctx.shadowBlur = 0
        } else if (isHighlighted) {
          ctx.fillStyle = '#38bdf8'
          ctx.shadowColor = 'rgba(56, 189, 248, 0.8)'
          ctx.shadowBlur = 16
        } else if (node.is_critical) {
          ctx.fillStyle = '#ef4444'
          ctx.shadowColor = 'rgba(239, 68, 68, 0.7)'
          ctx.shadowBlur = 12
        } else {
          ctx.fillStyle = '#6366f1'
          ctx.shadowColor = 'rgba(99, 102, 241, 0.5)'
          ctx.shadowBlur = 8
        }
        ctx.fill()
        ctx.shadowBlur = 0

        if (node.is_critical && !isDimmed) {
          ctx.lineWidth = 2
          ctx.strokeStyle = '#fca5a5'
          ctx.stroke()
        }

        const fontSize = Math.max(9 / globalScale, 3)
        ctx.font = `500 ${fontSize}px Inter, sans-serif`
        ctx.fillStyle = isDimmed ? 'rgba(148, 163, 184, 0.3)' : isHighlighted ? '#38bdf8' : '#f1f5f9'
        ctx.textAlign = 'center'
        ctx.textBaseline = 'top'
        ctx.fillText(node.id, node.x, node.y + radius + 3)
      }}
      nodePointerAreaPaint={(nodeRaw, color, ctx) => {
        const node = nodeRaw as RenderNode & { x?: number; y?: number }
        if (node.x == null || node.y == null) return
        const betweenness = centralityByName.get(node.id) ?? 0
        const radius = 5 + 15 * (betweenness / maxBetweenness)
        ctx.fillStyle = color
        ctx.beginPath()
        ctx.arc(node.x, node.y, radius + 2, 0, 2 * Math.PI)
        ctx.fill()
      }}
    />
  )
}
