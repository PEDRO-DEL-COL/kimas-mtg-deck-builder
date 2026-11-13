import type { CardSearchState } from '../hooks/useCardSearch.ts'
import type { CardSummary } from '../api/cards.ts'

interface Props {
  state: CardSearchState
  page: number
  onPage: (page: number) => void
  onSelect: (card: CardSummary) => void
}

const pageButton =
  'rounded-card border border-border px-4 py-2 text-sm font-semibold hover:border-primary disabled:cursor-not-allowed disabled:opacity-40'
const gridClass =
  'grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4 xl:grid-cols-5 2xl:grid-cols-6'

function CardTile({ card, onSelect }: { card: CardSummary; onSelect: (c: CardSummary) => void }) {
  return (
    <li>
      <button
        type="button"
        onClick={() => onSelect(card)}
        title={card.name}
        className="block w-full overflow-hidden rounded-[4.75%/3.4%] transition-transform hover:-translate-y-0.5 hover:shadow-card focus-visible:outline-2 focus-visible:outline-primary"
      >
        {card.image_url ? (
          <img
            src={card.image_url}
            alt={card.name}
            loading="lazy"
            className="block aspect-[488/680] w-full bg-surface object-cover"
          />
        ) : (
          <span className="flex aspect-[488/680] w-full flex-col items-center justify-center gap-1 border border-border bg-surface p-2 text-center text-sm font-semibold">
            {card.name}
            <span className="text-xs font-normal text-muted">{card.type_line}</span>
          </span>
        )}
      </button>
    </li>
  )
}

export default function CardGrid({ state, page, onPage, onSelect }: Props) {
  const { data, loading, error } = state

  if (error) {
    return (
      <div role="alert" className="rounded-card border border-danger/50 bg-surface p-6 text-danger">
        Não foi possível carregar as cartas. A API está rodando?
      </div>
    )
  }

  if (!data) {
    return (
      <ul className={gridClass} aria-busy="true" aria-label="Carregando cartas">
        {Array.from({ length: 12 }, (_, i) => (
          <li key={i} className="aspect-[488/680] animate-pulse rounded-card bg-surface" />
        ))}
      </ul>
    )
  }

  const totalPages = Math.max(1, Math.ceil(data.total / data.page_size))

  return (
    <div className="space-y-4">
      <p aria-live="polite" className="text-sm text-muted">
        {data.total === 1
          ? '1 carta encontrada'
          : `${data.total.toLocaleString('pt-BR')} cartas encontradas`}
      </p>

      {data.items.length === 0 ? (
        <div className="rounded-card border border-border bg-surface p-8 text-center text-muted">
          Nenhuma carta encontrada. Tente ajustar os filtros.
        </div>
      ) : (
        <ul
          className={`${gridClass} transition-opacity ${loading ? 'opacity-50' : ''}`}
          aria-busy={loading}
        >
          {data.items.map((card) => (
            <CardTile key={card.id} card={card} onSelect={onSelect} />
          ))}
        </ul>
      )}

      {data.total > 0 && (
        <nav aria-label="Paginação" className="flex items-center justify-center gap-4 pt-2">
          <button
            type="button"
            className={pageButton}
            disabled={page <= 1}
            onClick={() => onPage(page - 1)}
          >
            Anterior
          </button>
          <span className="text-sm text-muted">
            Página {data.page} de {totalPages}
          </span>
          <button
            type="button"
            className={pageButton}
            disabled={page >= totalPages}
            onClick={() => onPage(page + 1)}
          >
            Próxima
          </button>
        </nav>
      )}
    </div>
  )
}
