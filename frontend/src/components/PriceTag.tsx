import { formatDate } from '../lib/format.ts'

interface PriceTagProps {
  amount: string | number | null
  currency: 'USD' | 'BRL'
  source: string
  /** ISO date string of when the price was collected. */
  collectedAt: string | null
  /** When defined, colors green (within budget) or red (over budget). */
  overBudget?: boolean
  label?: string
  /** Smaller text for dense lists. */
  compact?: boolean
}

function formatAmount(amount: string | number, currency: 'USD' | 'BRL'): string | null {
  const n = typeof amount === 'number' ? amount : Number(amount)
  if (!Number.isFinite(n)) return null
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency }).format(n)
}

export default function PriceTag({
  amount,
  currency,
  source,
  collectedAt,
  overBudget,
  label,
  compact = false,
}: PriceTagProps) {
  const formatted = amount === null ? null : formatAmount(amount, currency)
  const date = collectedAt ? formatDate(collectedAt) : ''
  const color = overBudget === undefined ? 'text-text' : overBudget ? 'text-danger' : 'text-success'

  if (formatted === null) {
    return (
      <span className={`${compact ? 'text-xs' : 'text-sm'} text-muted`}>
        {label ? `${label}: ` : ''}Sem preço
      </span>
    )
  }

  return (
    <span className={compact ? 'text-xs' : 'text-sm'}>
      {label && <span className="text-muted">{label}: </span>}
      <span className={`font-mono font-semibold ${color}`}>{formatted}</span>{' '}
      <span className="text-muted">
        ({source}){date && ` · ${date}`}
      </span>
    </span>
  )
}
