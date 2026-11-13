interface PriceTagProps {
  /** Price in BRL. */
  value: number
  /** ISO date string or Date of when the price was collected. */
  collectedAt: string | Date
  /** True when the price exceeds the Commander 10 budget. */
  overBudget?: boolean
}

const currency = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' })
const dateFormat = new Intl.DateTimeFormat('pt-BR', {
  day: '2-digit',
  month: '2-digit',
  year: 'numeric',
})

export default function PriceTag({ value, collectedAt, overBudget = false }: PriceTagProps) {
  return (
    <div className="inline-flex flex-col">
      <span
        className={`font-mono text-base font-semibold ${overBudget ? 'text-danger' : 'text-success'}`}
      >
        {currency.format(value)}
      </span>
      <span className="text-xs text-muted">
        Preço LigaMagic em {dateFormat.format(new Date(collectedAt))}
      </span>
    </div>
  )
}
