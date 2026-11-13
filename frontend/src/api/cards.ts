const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export type SetMode = 'subset' | 'exact' | 'superset'

export interface CardSummary {
  id: string
  oracle_id: string
  name: string
  printed_name_pt: string | null
  mana_cost: string | null
  cmc: number
  type_line: string
  colors: string[]
  color_identity: string[]
  rarity: string | null
  legal_commander: boolean
  image_url: string | null
}

export interface CardDetail extends CardSummary {
  oracle_text: string | null
  scryfall_uri: string | null
}

export interface CardSearchResponse {
  items: CardSummary[]
  total: number
  page: number
  page_size: number
}

export interface CardSearchParams {
  q?: string
  identity?: string
  identity_mode?: SetMode
  colors?: string
  colors_mode?: SetMode
  type?: string
  subtype?: string
  cmc_min?: number
  cmc_max?: number
  text?: string
  rarity?: string
  commander_legal?: boolean
  sort?: 'name' | 'cmc'
  page?: number
  page_size?: number
}

export class ApiError extends Error {
  readonly status: number

  constructor(status: number, message: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

export function buildQueryString(params: CardSearchParams): string {
  const search = new URLSearchParams()
  for (const [key, value] of Object.entries(params)) {
    if (value === undefined || value === null || value === '') continue
    if (typeof value === 'number' && Number.isNaN(value)) continue
    search.set(key, String(value))
  }
  const text = search.toString()
  return text ? `?${text}` : ''
}

async function request<T>(path: string, signal?: AbortSignal): Promise<T> {
  const response = await fetch(`${BASE_URL}${path}`, {
    signal,
    headers: { Accept: 'application/json' },
  })
  if (!response.ok) {
    let detail = response.statusText
    try {
      const body = (await response.json()) as { detail?: unknown }
      if (typeof body.detail === 'string') detail = body.detail
    } catch {
      // body is not JSON; keep status text
    }
    throw new ApiError(response.status, detail)
  }
  return (await response.json()) as T
}

export function searchCards(
  params: CardSearchParams,
  signal?: AbortSignal,
): Promise<CardSearchResponse> {
  return request<CardSearchResponse>(`/api/cards${buildQueryString(params)}`, signal)
}

export function getCard(id: string, signal?: AbortSignal): Promise<CardDetail> {
  return request<CardDetail>(`/api/cards/${encodeURIComponent(id)}`, signal)
}
