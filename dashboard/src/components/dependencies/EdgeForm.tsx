import { zodResolver } from '@hookform/resolvers/zod'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { useAddEdge } from '../../hooks/useFingraph'
import type { DependencyNode } from '../../types/fingraph'

const edgeSchema = z.object({
  from_name: z.string().min(1, 'Required'),
  to_name: z.string().min(1, 'Required'),
})

type EdgeFormValues = z.infer<typeof edgeSchema>

export function EdgeForm({ orgId, nodes }: { orgId: string; nodes: DependencyNode[] }) {
  const addEdge = useAddEdge(orgId)
  const [cycleError, setCycleError] = useState<string | null>(null)
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<EdgeFormValues>({ resolver: zodResolver(edgeSchema) })

  async function onSubmit(values: EdgeFormValues) {
    setCycleError(null)
    try {
      await addEdge.mutateAsync(values)
      reset()
    } catch (err: unknown) {
      // The backend rejects an edge that would create a dependency cycle
      // with a 409 and a clear message (app.modules.org.fingraph.graph_management.CycleError)
      // -- surface that verbatim rather than a generic "something went wrong."
      const message =
        (err as { response?: { data?: { error?: { message?: string } } } })?.response?.data?.error?.message ??
        'Could not add edge.'
      setCycleError(message)
    }
  }

  return (
    <form className="graph-form" onSubmit={handleSubmit(onSubmit)}>
      <h3>Add edge (depends on)</h3>
      <label>
        From
        <select {...register('from_name')}>
          <option value="">Select…</option>
          {nodes.map((n) => (
            <option key={n.id} value={n.name}>
              {n.name}
            </option>
          ))}
        </select>
        {errors.from_name && <span className="graph-form__error">{errors.from_name.message}</span>}
      </label>
      <label>
        Depends on
        <select {...register('to_name')}>
          <option value="">Select…</option>
          {nodes.map((n) => (
            <option key={n.id} value={n.name}>
              {n.name}
            </option>
          ))}
        </select>
        {errors.to_name && <span className="graph-form__error">{errors.to_name.message}</span>}
      </label>
      <button type="submit" disabled={addEdge.isPending}>
        Add edge
      </button>
      {cycleError && <p className="graph-form__error" role="alert">{cycleError}</p>}
    </form>
  )
}
