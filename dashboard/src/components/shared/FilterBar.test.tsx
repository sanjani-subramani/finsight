import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it } from 'vitest'
import { MemoryRouter, useLocation } from 'react-router-dom'
import { FilterBar } from './FilterBar'

function LocationDisplay() {
  const location = useLocation()
  return <div data-testid="location-search">{location.search}</div>
}

function renderWithRouter() {
  return render(
    <MemoryRouter initialEntries={['/transactions']}>
      <FilterBar
        fields={[
          { key: 'provider', label: 'Provider', type: 'text' },
          {
            key: 'status',
            label: 'Status',
            type: 'select',
            options: [{ value: 'bank_failed', label: 'Bank failed' }],
          },
        ]}
      />
      <LocationDisplay />
    </MemoryRouter>,
  )
}

describe('FilterBar', () => {
  it('writes filter changes into the URL query string', async () => {
    const user = userEvent.setup()
    renderWithRouter()

    await user.type(screen.getByLabelText('Provider'), 'razorpay')

    const search = screen.getByTestId('location-search').textContent ?? ''
    expect(new URLSearchParams(search).get('provider')).toBe('razorpay')
  })

  it('restores filter state from an existing URL (round-trip)', () => {
    render(
      <MemoryRouter initialEntries={['/transactions?provider=razorpay&status=bank_failed']}>
        <FilterBar
          fields={[
            { key: 'provider', label: 'Provider', type: 'text' },
            {
              key: 'status',
              label: 'Status',
              type: 'select',
              options: [{ value: 'bank_failed', label: 'Bank failed' }],
            },
          ]}
        />
      </MemoryRouter>,
    )

    expect(screen.getByLabelText('Provider')).toHaveValue('razorpay')
    expect(screen.getByLabelText('Status')).toHaveValue('bank_failed')
  })

  it('"Clear filters" removes every filter from the URL', async () => {
    const user = userEvent.setup()
    render(
      <MemoryRouter initialEntries={['/transactions?provider=razorpay']}>
        <FilterBar fields={[{ key: 'provider', label: 'Provider', type: 'text' }]} />
        <LocationDisplay />
      </MemoryRouter>,
    )

    await user.click(screen.getByText('Clear filters'))
    expect(screen.getByTestId('location-search').textContent).toBe('')
  })
})
