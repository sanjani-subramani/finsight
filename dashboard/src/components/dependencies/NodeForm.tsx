import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { useAddNode } from '../../hooks/useFingraph'

const nodeSchema = z.object({
  name: z.string().min(1, 'Name is required'),
  node_type: z.string().min(1, 'Type is required'),
  is_critical: z.boolean(),
})

type NodeFormValues = z.infer<typeof nodeSchema>

export function NodeForm({ orgId }: { orgId: string }) {
  const addNode = useAddNode(orgId)
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<NodeFormValues>({
    resolver: zodResolver(nodeSchema),
    defaultValues: { name: '', node_type: 'service', is_critical: false },
  })

  async function onSubmit(values: NodeFormValues) {
    await addNode.mutateAsync(values)
    reset()
  }

  return (
    <form className="graph-form" onSubmit={handleSubmit(onSubmit)}>
      <h3>Add node</h3>
      <label>
        Name
        <input {...register('name')} />
        {errors.name && <span className="graph-form__error">{errors.name.message}</span>}
      </label>
      <label>
        Type
        <select {...register('node_type')}>
          <option value="service">service</option>
          <option value="workflow">workflow</option>
        </select>
      </label>
      <label className="graph-form__checkbox">
        <input type="checkbox" {...register('is_critical')} />
        Critical
      </label>
      <button type="submit" disabled={addNode.isPending}>
        Add node
      </button>
      {addNode.isError && <p className="graph-form__error">Could not add node.</p>}
    </form>
  )
}
