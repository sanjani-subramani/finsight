import {
  flexRender,
  getCoreRowModel,
  getSortedRowModel,
  useReactTable,
  type ColumnDef,
  type SortingState,
} from '@tanstack/react-table'
import { useState } from 'react'
import './DataTable.css'

export interface DataTableProps<T> {
  data: T[]
  columns: ColumnDef<T, any>[]
  onRowClick?: (row: T) => void
  isLoading?: boolean
  emptyMessage?: string
  /** Server-side pagination: when provided, DataTable renders Prev/Next
   * controls that call onPageChange instead of paginating client-side --
   * required for PayTrace transaction search / ReconX mismatches, which
   * can be far too large to fetch in one request. */
  pagination?: {
    pageIndex: number
    pageSize: number
    total: number
    onPageChange: (pageIndex: number) => void
  }
  getRowId?: (row: T) => string
}

export function DataTable<T>({
  data,
  columns,
  onRowClick,
  isLoading,
  emptyMessage = 'No results.',
  pagination,
  getRowId,
}: DataTableProps<T>) {
  const [sorting, setSorting] = useState<SortingState>([])

  const table = useReactTable({
    data,
    columns,
    state: { sorting },
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getRowId: getRowId as ((row: T) => string) | undefined,
  })

  const pageCount = pagination ? Math.max(1, Math.ceil(pagination.total / pagination.pageSize)) : null

  return (
    <div className="data-table">
      <table>
        <thead>
          {table.getHeaderGroups().map((headerGroup) => (
            <tr key={headerGroup.id}>
              {headerGroup.headers.map((header) => (
                <th
                  key={header.id}
                  onClick={header.column.getToggleSortingHandler()}
                  className={header.column.getCanSort() ? 'data-table__sortable' : undefined}
                >
                  {header.isPlaceholder ? null : flexRender(header.column.columnDef.header, header.getContext())}
                  {{ asc: ' ↑', desc: ' ↓' }[header.column.getIsSorted() as string] ?? ''}
                </th>
              ))}
            </tr>
          ))}
        </thead>
        <tbody>
          {isLoading && (
            <tr>
              <td colSpan={columns.length} className="data-table__status">
                Loading…
              </td>
            </tr>
          )}
          {!isLoading && data.length === 0 && (
            <tr>
              <td colSpan={columns.length} className="data-table__status">
                {emptyMessage}
              </td>
            </tr>
          )}
          {!isLoading &&
            table.getRowModel().rows.map((row) => (
              <tr
                key={row.id}
                onClick={onRowClick ? () => onRowClick(row.original) : undefined}
                className={onRowClick ? 'data-table__row--clickable' : undefined}
              >
                {row.getVisibleCells().map((cell) => (
                  <td key={cell.id}>{flexRender(cell.column.columnDef.cell, cell.getContext())}</td>
                ))}
              </tr>
            ))}
        </tbody>
      </table>

      {pagination && pageCount !== null && (
        <div className="data-table__pagination">
          <button
            type="button"
            onClick={() => pagination.onPageChange(pagination.pageIndex - 1)}
            disabled={pagination.pageIndex <= 0}
          >
            Previous
          </button>
          <span>
            Page {pagination.pageIndex + 1} of {pageCount} ({pagination.total} total)
          </span>
          <button
            type="button"
            onClick={() => pagination.onPageChange(pagination.pageIndex + 1)}
            disabled={pagination.pageIndex + 1 >= pageCount}
          >
            Next
          </button>
        </div>
      )}
    </div>
  )
}
