import { useState } from 'react'
import type { SetMode } from '../api/cards.ts'
import {
  COLOR_NAMES,
  COLOR_ORDER,
  EMPTY_FILTERS,
  RARITIES,
  RARITY_LABELS,
  hasActiveFilters,
} from '../lib/filters.ts'
import type { SearchFilters } from '../lib/filters.ts'

interface Props {
  filters: SearchFilters
  onChange: (patch: Partial<SearchFilters>) => void
  onReset: () => void
}

const TYPES: [string, string][] = [
  ['Criatura', 'Creature'],
  ['Instantâneo', 'Instant'],
  ['Feitiço', 'Sorcery'],
  ['Artefato', 'Artifact'],
  ['Encantamento', 'Enchantment'],
  ['Planeswalker', 'Planeswalker'],
  ['Terreno', 'Land'],
  ['Batalha', 'Battle'],
  ['Lendário', 'Legendary'],
]

const MODES: [SetMode, string][] = [
  ['subset', 'Dentro da identidade'],
  ['exact', 'Exata'],
  ['superset', 'Inclui'],
]

const COLOR_STYLES: Record<string, { on: string; off: string }> = {
  W: {
    on: 'border-amber-100 bg-amber-100/25 text-amber-50',
    off: 'border-amber-100/30 text-amber-100/80 hover:bg-amber-100/10',
  },
  U: {
    on: 'border-sky-400 bg-sky-500/30 text-sky-100',
    off: 'border-sky-400/30 text-sky-300 hover:bg-sky-500/10',
  },
  B: {
    on: 'border-fuchsia-300 bg-fuchsia-950 text-fuchsia-100',
    off: 'border-fuchsia-300/30 text-fuchsia-200/80 hover:bg-fuchsia-500/10',
  },
  R: {
    on: 'border-red-400 bg-red-500/30 text-red-100',
    off: 'border-red-400/30 text-red-300 hover:bg-red-500/10',
  },
  G: {
    on: 'border-green-400 bg-green-500/30 text-green-100',
    off: 'border-green-400/30 text-green-300 hover:bg-green-500/10',
  },
  C: {
    on: 'border-zinc-300 bg-zinc-400/25 text-zinc-100',
    off: 'border-zinc-400/30 text-zinc-300 hover:bg-zinc-400/10',
  },
}

const inputClass =
  'w-full rounded-card border border-border bg-background px-3 py-2 text-sm text-text placeholder:text-muted focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary'
const labelClass = 'mb-1 block text-sm font-medium text-text'
const hintClass = 'mt-1 text-xs text-muted'

function toggleColor(selected: string[], letter: string): string[] {
  if (selected.includes(letter)) return selected.filter((c) => c !== letter)
  if (letter === 'C') return ['C']
  return COLOR_ORDER.filter((c) => c !== 'C' && (c === letter || selected.includes(c)))
}

interface ColorPickerProps {
  legend: string
  selected: string[]
  mode: SetMode
  onSelected: (value: string[]) => void
  onMode: (value: SetMode) => void
}

function ColorPicker({ legend, selected, mode, onSelected, onMode }: ColorPickerProps) {
  return (
    <fieldset>
      <legend className={labelClass}>{legend}</legend>
      <div className="flex flex-wrap gap-1.5">
        {COLOR_ORDER.map((letter) => {
          const active = selected.includes(letter)
          const style = COLOR_STYLES[letter]
          return (
            <button
              key={letter}
              type="button"
              aria-pressed={active}
              title={COLOR_NAMES[letter]}
              aria-label={COLOR_NAMES[letter]}
              onClick={() => onSelected(toggleColor(selected, letter))}
              className={`h-9 rounded-full border text-sm font-bold transition-colors ${
                letter === 'C' ? 'px-3 font-semibold' : 'w-9'
              } ${active ? style.on : style.off}`}
            >
              {letter === 'C' ? 'Incolor' : letter}
            </button>
          )
        })}
      </div>
      <select
        aria-label={`Modo: ${legend}`}
        value={mode}
        onChange={(e) => onMode(e.target.value as SetMode)}
        className={`${inputClass} mt-2`}
      >
        {MODES.map(([value, label]) => (
          <option key={value} value={value}>
            {label}
          </option>
        ))}
      </select>
    </fieldset>
  )
}

export default function CardFilters({ filters, onChange, onReset }: Props) {
  const [open, setOpen] = useState(false)

  return (
    <section
      aria-label="Filtros de busca"
      className="rounded-card border border-border bg-surface shadow-card"
    >
      <button
        type="button"
        aria-expanded={open}
        aria-controls="card-filters-body"
        onClick={() => setOpen((v) => !v)}
        className="flex w-full items-center justify-between px-4 py-3 text-left font-semibold lg:hidden"
      >
        Filtros{hasActiveFilters(filters) ? ' (ativos)' : ''}
        <span aria-hidden="true">{open ? '−' : '+'}</span>
      </button>

      <div
        id="card-filters-body"
        className={`${open ? 'block' : 'hidden'} space-y-4 border-t border-border p-4 lg:block lg:border-t-0`}
      >
        <div>
          <label htmlFor="f-q" className={labelClass}>
            Nome
          </label>
          <input
            id="f-q"
            type="search"
            value={filters.q}
            onChange={(e) => onChange({ q: e.target.value })}
            placeholder="Nome da carta"
            className={inputClass}
          />
        </div>

        <ColorPicker
          legend="Identidade de cor"
          selected={filters.identity}
          mode={filters.identityMode}
          onSelected={(identity) => onChange({ identity })}
          onMode={(identityMode) => onChange({ identityMode })}
        />

        <ColorPicker
          legend="Cores do custo"
          selected={filters.colors}
          mode={filters.colorsMode}
          onSelected={(colors) => onChange({ colors })}
          onMode={(colorsMode) => onChange({ colorsMode })}
        />

        <div>
          <label htmlFor="f-type" className={labelClass}>
            Tipo
          </label>
          <select
            id="f-type"
            value={filters.type}
            onChange={(e) => onChange({ type: e.target.value })}
            className={inputClass}
          >
            <option value="">Todos</option>
            {TYPES.map(([label, value]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label htmlFor="f-subtype" className={labelClass}>
            Subtipo
          </label>
          <input
            id="f-subtype"
            type="text"
            value={filters.subtype}
            onChange={(e) => onChange({ subtype: e.target.value })}
            className={inputClass}
          />
          <p className={hintClass}>em inglês, ex.: Elf</p>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <label htmlFor="f-cmc-min" className={labelClass}>
              CMC mín.
            </label>
            <input
              id="f-cmc-min"
              type="number"
              min={0}
              value={filters.cmcMin}
              onChange={(e) => onChange({ cmcMin: e.target.value })}
              className={inputClass}
            />
          </div>
          <div>
            <label htmlFor="f-cmc-max" className={labelClass}>
              CMC máx.
            </label>
            <input
              id="f-cmc-max"
              type="number"
              min={0}
              value={filters.cmcMax}
              onChange={(e) => onChange({ cmcMax: e.target.value })}
              className={inputClass}
            />
          </div>
        </div>

        <div>
          <label htmlFor="f-text" className={labelClass}>
            Texto da carta
          </label>
          <input
            id="f-text"
            type="text"
            value={filters.text}
            onChange={(e) => onChange({ text: e.target.value })}
            className={inputClass}
          />
          <p className={hintClass}>texto oracle, em inglês, ex.: draw a card</p>
        </div>

        <fieldset>
          <legend className={labelClass}>Raridade</legend>
          <div className="grid grid-cols-2 gap-1">
            {RARITIES.map((r) => (
              <label key={r} className="flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={filters.rarity.includes(r)}
                  onChange={(e) =>
                    onChange({
                      rarity: e.target.checked
                        ? RARITIES.filter((x) => x === r || filters.rarity.includes(x))
                        : filters.rarity.filter((x) => x !== r),
                    })
                  }
                  className="accent-primary"
                />
                {RARITY_LABELS[r]}
              </label>
            ))}
          </div>
        </fieldset>

        <label className="flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={filters.commanderLegal}
            onChange={(e) => onChange({ commanderLegal: e.target.checked })}
            className="accent-primary"
          />
          Somente legais no Commander
        </label>

        <div>
          <label htmlFor="f-sort" className={labelClass}>
            Ordenar por
          </label>
          <select
            id="f-sort"
            value={filters.sort}
            onChange={(e) => onChange({ sort: e.target.value as SearchFilters['sort'] })}
            className={inputClass}
          >
            <option value="name">Nome</option>
            <option value="cmc">CMC</option>
          </select>
        </div>

        <button
          type="button"
          onClick={onReset}
          disabled={JSON.stringify(filters) === JSON.stringify(EMPTY_FILTERS)}
          className="w-full rounded-card border border-border px-4 py-2 text-sm font-semibold text-text hover:border-primary disabled:cursor-not-allowed disabled:opacity-50"
        >
          Limpar filtros
        </button>
      </div>
    </section>
  )
}
