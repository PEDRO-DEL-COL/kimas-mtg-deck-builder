import { useEffect, useRef, useState } from 'react'
import { getCard } from '../api/cards.ts'
import type { CardDetail as CardDetailData } from '../api/cards.ts'
import PriceTag from './PriceTag.tsx'
import { COLOR_NAMES, RARITY_LABELS } from '../lib/filters.ts'

interface Props {
  cardId: string
  onClose: () => void
}

interface Result {
  id: string
  card: CardDetailData | null
  error: boolean
}

const FOCUSABLE =
  'a[href], button:not([disabled]), input, select, textarea, [tabindex]:not([tabindex="-1"])'

export default function CardDetail({ cardId, onClose }: Props) {
  const [result, setResult] = useState<Result | null>(null)
  const dialogRef = useRef<HTMLDivElement>(null)
  const closeRef = useRef<HTMLButtonElement>(null)
  const onCloseRef = useRef(onClose)

  useEffect(() => {
    onCloseRef.current = onClose
  })

  useEffect(() => {
    const controller = new AbortController()
    getCard(cardId, controller.signal)
      .then((card) => setResult({ id: cardId, card, error: false }))
      .catch(() => {
        if (!controller.signal.aborted) setResult({ id: cardId, card: null, error: true })
      })
    return () => controller.abort()
  }, [cardId])

  useEffect(() => {
    const previous = document.activeElement as HTMLElement | null
    const overflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    closeRef.current?.focus()

    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onCloseRef.current()
        return
      }
      if (e.key !== 'Tab' || !dialogRef.current) return
      const items = Array.from(dialogRef.current.querySelectorAll<HTMLElement>(FOCUSABLE))
      if (items.length === 0) return
      const first = items[0]
      const last = items[items.length - 1]
      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault()
        last.focus()
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault()
        first.focus()
      }
    }
    document.addEventListener('keydown', onKeyDown)
    return () => {
      document.removeEventListener('keydown', onKeyDown)
      document.body.style.overflow = overflow
      previous?.focus()
    }
  }, [])

  const loaded = result !== null && result.id === cardId
  const card = loaded ? result.card : null
  const failed = loaded && result.error

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center overflow-y-auto bg-black/75 p-4"
      onMouseDown={(e) => {
        if (e.target === e.currentTarget) onClose()
      }}
    >
      <div
        ref={dialogRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby="card-detail-title"
        className="relative my-auto w-full max-w-3xl rounded-card border border-border bg-surface p-5 shadow-card"
      >
        <button
          ref={closeRef}
          type="button"
          onClick={onClose}
          aria-label="Fechar"
          className="absolute right-3 top-3 rounded-full border border-border px-3 py-1 text-sm hover:border-primary"
        >
          ✕
        </button>

        {failed && (
          <p id="card-detail-title" role="alert" className="py-10 text-center text-danger">
            Não foi possível carregar a carta.
          </p>
        )}

        {!loaded && (
          <p id="card-detail-title" className="py-10 text-center text-muted">
            Carregando…
          </p>
        )}

        {card && (
          <div className="grid gap-5 sm:grid-cols-[minmax(0,16rem)_1fr]">
            {card.image_url ? (
              <img
                src={card.image_url}
                alt={card.name}
                className="aspect-[488/680] w-full max-w-xs justify-self-center rounded-[4.75%/3.4%]"
              />
            ) : (
              <div className="flex aspect-[488/680] w-full items-center justify-center rounded-card border border-border p-3 text-center font-semibold">
                {card.name}
              </div>
            )}
            <div className="space-y-3 pr-8">
              <h2 id="card-detail-title" className="text-2xl font-bold">
                {card.name}
              </h2>
              {card.printed_name_pt && card.printed_name_pt !== card.name && (
                <p className="text-sm text-muted">{card.printed_name_pt}</p>
              )}
              {card.mana_cost && <p className="font-mono text-primary-hover">{card.mana_cost}</p>}
              <p className="text-sm">{card.type_line}</p>
              {card.oracle_text && (
                <p className="whitespace-pre-line rounded-card border border-border bg-background p-3 text-sm">
                  {card.oracle_text}
                </p>
              )}
              <dl className="grid grid-cols-[auto_1fr] gap-x-4 gap-y-1 text-sm">
                <dt className="text-muted">Raridade</dt>
                <dd>{card.rarity ? (RARITY_LABELS[card.rarity] ?? card.rarity) : '—'}</dd>
                <dt className="text-muted">Legal no Commander</dt>
                <dd className={card.legal_commander ? 'text-success' : 'text-danger'}>
                  {card.legal_commander ? 'Sim' : 'Não'}
                </dd>
                <dt className="text-muted">Identidade de cor</dt>
                <dd>
                  {card.color_identity.length > 0
                    ? card.color_identity.map((c) => COLOR_NAMES[c] ?? c).join(', ')
                    : 'Incolor'}
                </dd>
              </dl>
              <div className="space-y-1">
                {(
                  [
                    ['Normal', card.price_usd],
                    ['Foil', card.price_usd_foil],
                    ['Etched', card.price_usd_etched],
                  ] as const
                )
                  .filter(([label, amount]) => label === 'Normal' || amount !== null)
                  .map(([label, amount]) => (
                    <div key={label}>
                      <PriceTag
                        label={label}
                        amount={amount}
                        currency={card.price_currency}
                        source={card.price_source}
                        collectedAt={card.prices_updated_at}
                      />
                    </div>
                  ))}
                <p className="text-xs text-muted">
                  Preço em dólar americano fornecido pelo Scryfall. Estimativa em reais (R$) ainda
                  não disponível.
                </p>
              </div>
              {card.scryfall_uri && (
                <a
                  href={card.scryfall_uri}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-block text-sm text-primary-hover underline-offset-2 hover:underline"
                >
                  Ver no Scryfall
                </a>
              )}
            </div>
          </div>
        )}

        <p className="mt-5 border-t border-border pt-3 text-xs text-muted">
          Dados e imagem da carta: Scryfall. Magic: The Gathering © Wizards of the Coast.
        </p>
      </div>
    </div>
  )
}
