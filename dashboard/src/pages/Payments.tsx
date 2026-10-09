import { useMemo, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { useOrgAuth } from '../auth/useOrgAuth'
import { ProviderAlertBanner } from '../components/payments/ProviderAlertBanner'
import { TransactionDrawer } from '../components/payments/TransactionDrawer'
import { DataTable } from '../components/shared/DataTable'
import { FilterBar } from '../components/shared/FilterBar'
import { StatCard } from '../components/shared/StatCard'
import { usePaymentHealth, useProviderAlerts, useProviderStats, useTransactionSearch } from '../hooks/usePaytrace'
import type { FailureMode, TransactionSummary, TxnStage } from '../types/paytrace'
import type { ColumnDef } from '@tanstack/react-table'

const PAGE_SIZE = 25

const STATUS_OPTIONS = [
  'initiated',
  'gateway_accepted',
  'gateway_failed',
  'bank_accepted',
  'bank_failed',
  'webhook_sent',
  'webhook_failed',
  'settled',
  'settlement_failed',
  'refunded',
].map((value) => ({ value, label: value.replace(/_/g, ' ') }))

const FAILURE_MODE_OPTIONS = [
  'successful',
  'gateway_timeout',
  'bank_declined',
  'webhook_lost',
  'settlement_delayed',
  'duplicate_attempt',
  'partial_failure',
  'stuck',
  'reversed',
  'other_failure',
  'in_progress',
].map((value) => ({ value, label: value.replace(/_/g, ' ') }))

const columns: ColumnDef<TransactionSummary, any>[] = [
  { accessorKey: 'transaction_ref', header: 'Ref' },
  { accessorKey: 'current_stage', header: 'Stage' },
  { accessorKey: 'provider', header: 'Provider' },
  { accessorKey: 'failure_mode', header: 'Classification' },
  {
    accessorKey: 'last_event_at',
    header: 'Last event',
    cell: (info) => {
      const value = info.getValue<string | null>()
      return value ? new Date(value).toLocaleString() : '—'
    },
  },
]

export function Payments() {
  const { currentOrgId } = useOrgAuth()
  const orgId = currentOrgId as string
  const [searchParams] = useSearchParams()
  const [page, setPage] = useState(0)
  const [selectedRef, setSelectedRef] = useState<string | null>(null)

  const filters = useMemo(
    () => ({
      status: (searchParams.get('status') as TxnStage | null) || undefined,
      provider: searchParams.get('provider') || undefined,
      date_from: searchParams.get('date_from') || undefined,
      date_to: searchParams.get('date_to') || undefined,
      failure_mode: (searchParams.get('failure_mode') as FailureMode | null) || undefined,
      limit: PAGE_SIZE,
      offset: page * PAGE_SIZE,
    }),
    [searchParams, page],
  )

  const healthQuery = usePaymentHealth(orgId)
  const providersQuery = useProviderStats(orgId)
  const alertsQuery = useProviderAlerts(orgId)
  const searchQuery = useTransactionSearch(orgId, filters)

  const chartData = (providersQuery.data ?? []).map((p) => ({
    provider: p.provider,
    successRate: Math.round(p.success_rate * 1000) / 10,
  }))

  return (
    <div className="payments-page">
      <h1>Payments</h1>

      {alertsQuery.data?.map((alert) => <ProviderAlertBanner key={alert.provider} alert={alert} />)}

      <div className="stat-row">
        <StatCard
          label="Success rate"
          value={healthQuery.data ? `${(healthQuery.data.success_rate * 100).toFixed(1)}%` : '—'}
        />
        <StatCard label="Total transactions" value={healthQuery.data?.total_transactions ?? '—'} />
        <StatCard
          label="Webhook success rate"
          value={
            healthQuery.data?.webhook_success_rate != null
              ? `${(healthQuery.data.webhook_success_rate * 100).toFixed(1)}%`
              : 'n/a'
          }
        />
        <StatCard label="Anomalies" value={healthQuery.data?.anomaly_count ?? '—'} />
      </div>

      <div className="chart-panel glass-card" style={{ padding: 'var(--sp-5)', marginBottom: 'var(--sp-6)' }}>
        <h2 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: 'var(--sp-4)' }}>Success Rate by Provider</h2>
        <ResponsiveContainer width="100%" height={240}>
          <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="providerGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#818cf8" stopOpacity={0.9} />
                <stop offset="100%" stopColor="#6366f1" stopOpacity={0.6} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(148, 163, 184, 0.08)" vertical={false} />
            <XAxis
              dataKey="provider"
              stroke="var(--text-muted)"
              fontSize={12}
              tickLine={false}
              axisLine={{ stroke: 'rgba(148, 163, 184, 0.15)' }}
            />
            <YAxis
              unit="%"
              domain={[0, 100]}
              stroke="var(--text-muted)"
              fontSize={12}
              tickLine={false}
              axisLine={false}
            />
            <Tooltip
              formatter={(value) => [`${value}%`, 'Success Rate']}
              contentStyle={{
                background: 'rgba(15, 23, 42, 0.95)',
                backdropFilter: 'blur(10px)',
                border: '1px solid rgba(148, 163, 184, 0.2)',
                borderRadius: '8px',
                boxShadow: '0 8px 30px rgba(0, 0, 0, 0.5)',
                color: '#f1f5f9',
                fontSize: '0.8125rem',
              }}
              cursor={{ fill: 'rgba(99, 102, 241, 0.06)' }}
            />
            <Bar dataKey="successRate" fill="url(#providerGradient)" radius={[6, 6, 0, 0]} maxBarSize={55} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <FilterBar
        fields={[
          { key: 'status', label: 'Stage', type: 'select', options: STATUS_OPTIONS },
          { key: 'provider', label: 'Provider', type: 'text' },
          { key: 'date_from', label: 'From', type: 'date' },
          { key: 'date_to', label: 'To', type: 'date' },
          { key: 'failure_mode', label: 'Classification', type: 'select', options: FAILURE_MODE_OPTIONS },
        ]}
      />

      <DataTable
        data={searchQuery.data?.items ?? []}
        columns={columns}
        isLoading={searchQuery.isLoading}
        onRowClick={(row) => setSelectedRef(row.transaction_ref)}
        getRowId={(row) => row.transaction_ref}
        pagination={{
          pageIndex: page,
          pageSize: PAGE_SIZE,
          total: searchQuery.data?.total ?? 0,
          onPageChange: setPage,
        }}
      />

      {selectedRef && <TransactionDrawer orgId={orgId} transactionRef={selectedRef} onClose={() => setSelectedRef(null)} />}
    </div>
  )
}
