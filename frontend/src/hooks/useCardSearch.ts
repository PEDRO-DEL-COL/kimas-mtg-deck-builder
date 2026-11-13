import { useEffect, useState } from 'react'
import { searchCards } from '../api/cards.ts'
import type { CardSearchParams, CardSearchResponse } from '../api/cards.ts'

const DEBOUNCE_MS = 350

interface Result {
  key: string
  data: CardSearchResponse | null
  error: Error | null
}

export interface CardSearchState {
  data: CardSearchResponse | null
  loading: boolean
  error: Error | null
}

export function useCardSearch(params: CardSearchParams): CardSearchState {
  const key = JSON.stringify(params)
  const [debouncedKey, setDebouncedKey] = useState(key)
  const [result, setResult] = useState<Result | null>(null)

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedKey(key), DEBOUNCE_MS)
    return () => clearTimeout(timer)
  }, [key])

  useEffect(() => {
    const controller = new AbortController()
    const requestParams = JSON.parse(debouncedKey) as CardSearchParams
    searchCards(requestParams, controller.signal)
      .then((data) => setResult({ key: debouncedKey, data, error: null }))
      .catch((err: unknown) => {
        if (controller.signal.aborted) return
        const error = err instanceof Error ? err : new Error(String(err))
        setResult({ key: debouncedKey, data: null, error })
      })
    return () => controller.abort()
  }, [debouncedKey])

  const settled = result !== null && result.key === key
  return {
    data: result?.data ?? null,
    loading: !settled,
    error: settled ? result.error : null,
  }
}
