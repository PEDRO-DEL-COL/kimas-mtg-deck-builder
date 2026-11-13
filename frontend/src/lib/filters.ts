import type { CardSearchParams, SetMode } from '../api/cards.ts'

export interface SearchFilters {
  q: string
  identity: string[]
  identityMode: SetMode
  colors: string[]
  colorsMode: SetMode
  type: string
  subtype: string
  cmcMin: string
  cmcMax: string
  priceMin: string
  priceMax: string
  text: string
  rarity: string[]
  commanderLegal: boolean
  sort: 'name' | 'cmc' | 'price'
  page: number
}

export const PAGE_SIZE = 24
export const COLOR_ORDER = ['W', 'U', 'B', 'R', 'G', 'C']
export const RARITIES = ['common', 'uncommon', 'rare', 'mythic']

export const EMPTY_FILTERS: SearchFilters = {
  q: '',
  identity: [],
  identityMode: 'subset',
  colors: [],
  colorsMode: 'subset',
  type: '',
  subtype: '',
  cmcMin: '',
  cmcMax: '',
  priceMin: '',
  priceMax: '',
  text: '',
  rarity: [],
  commanderLegal: false,
  sort: 'name',
  page: 1,
}

function parseMode(value: string | null): SetMode {
  return value === 'exact' || value === 'superset' ? value : 'subset'
}

function parseSort(value: string | null): SearchFilters['sort'] {
  return value === 'cmc' || value === 'price' ? value : 'name'
}

function parseLetters(value: string | null): string[] {
  const letters = (value ?? '').toUpperCase().split('')
  return COLOR_ORDER.filter((c) => letters.includes(c))
}

export function filtersFromSearch(search: string): SearchFilters {
  const p = new URLSearchParams(search)
  const page = Number.parseInt(p.get('page') ?? '1', 10)
  return {
    q: p.get('q') ?? '',
    identity: parseLetters(p.get('identity')),
    identityMode: parseMode(p.get('identity_mode')),
    colors: parseLetters(p.get('colors')),
    colorsMode: parseMode(p.get('colors_mode')),
    type: p.get('type') ?? '',
    subtype: p.get('subtype') ?? '',
    cmcMin: p.get('cmc_min') ?? '',
    cmcMax: p.get('cmc_max') ?? '',
    priceMin: p.get('price_min') ?? '',
    priceMax: p.get('price_max') ?? '',
    text: p.get('text') ?? '',
    rarity: (p.get('rarity') ?? '').split(',').filter((r) => RARITIES.includes(r)),
    commanderLegal: p.get('commander_legal') === 'true',
    sort: parseSort(p.get('sort')),
    page: Number.isFinite(page) && page > 0 ? page : 1,
  }
}

function toNumber(value: string): number | undefined {
  if (value.trim() === '') return undefined
  const n = Number(value)
  return Number.isFinite(n) ? n : undefined
}

export function filtersToParams(f: SearchFilters): CardSearchParams {
  return {
    q: f.q.trim(),
    identity: f.identity.join(''),
    identity_mode: f.identity.length > 0 ? f.identityMode : undefined,
    colors: f.colors.join(''),
    colors_mode: f.colors.length > 0 ? f.colorsMode : undefined,
    type: f.type,
    subtype: f.subtype.trim(),
    cmc_min: toNumber(f.cmcMin),
    cmc_max: toNumber(f.cmcMax),
    price_min: toNumber(f.priceMin),
    price_max: toNumber(f.priceMax),
    text: f.text.trim(),
    rarity: f.rarity.join(','),
    commander_legal: f.commanderLegal ? true : undefined,
    sort: f.sort,
    page: f.page,
    page_size: PAGE_SIZE,
  }
}

/** Serializes filters to a URL query string (without leading "?"), omitting defaults. */
export function filtersToSearch(f: SearchFilters): string {
  const p = new URLSearchParams()
  const set = (key: string, value: string) => {
    if (value) p.set(key, value)
  }
  set('q', f.q)
  set('identity', f.identity.join(''))
  if (f.identity.length > 0 && f.identityMode !== 'subset') p.set('identity_mode', f.identityMode)
  set('colors', f.colors.join(''))
  if (f.colors.length > 0 && f.colorsMode !== 'subset') p.set('colors_mode', f.colorsMode)
  set('type', f.type)
  set('subtype', f.subtype)
  set('cmc_min', f.cmcMin)
  set('cmc_max', f.cmcMax)
  set('price_min', f.priceMin)
  set('price_max', f.priceMax)
  set('text', f.text)
  set('rarity', f.rarity.join(','))
  if (f.commanderLegal) p.set('commander_legal', 'true')
  if (f.sort !== 'name') p.set('sort', f.sort)
  if (f.page > 1) p.set('page', String(f.page))
  return p.toString()
}

export function hasActiveFilters(f: SearchFilters): boolean {
  return filtersToSearch({ ...f, sort: 'name', page: 1 }) !== ''
}

export const RARITY_LABELS: Record<string, string> = {
  common: 'Comum',
  uncommon: 'Incomum',
  rare: 'Rara',
  mythic: 'Mítica',
  special: 'Especial',
  bonus: 'Bônus',
}

export const COLOR_NAMES: Record<string, string> = {
  W: 'Branco',
  U: 'Azul',
  B: 'Preto',
  R: 'Vermelho',
  G: 'Verde',
  C: 'Incolor',
}
