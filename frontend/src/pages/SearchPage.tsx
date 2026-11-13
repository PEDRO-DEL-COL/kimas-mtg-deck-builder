import { useCallback, useState } from 'react'
import CardDetail from '../components/CardDetail.tsx'
import CardFilters from '../components/CardFilters.tsx'
import CardGrid from '../components/CardGrid.tsx'
import { useCardSearch } from '../hooks/useCardSearch.ts'
import {
  EMPTY_FILTERS,
  filtersFromSearch,
  filtersToParams,
  filtersToSearch,
} from '../lib/filters.ts'
import type { SearchFilters } from '../lib/filters.ts'

function initialFilters(): SearchFilters {
  const hash = window.location.hash
  const index = hash.indexOf('?')
  return filtersFromSearch(index >= 0 ? hash.slice(index + 1) : '')
}

export default function SearchPage() {
  const [filters, setFilters] = useState<SearchFilters>(initialFilters)
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const state = useCardSearch(filtersToParams(filters))

  const apply = useCallback((next: SearchFilters) => {
    setFilters(next)
    const query = filtersToSearch(next)
    const url = `${window.location.pathname}${window.location.search}#/busca${query ? `?${query}` : ''}`
    // replaceState does not fire hashchange, so App does not remount this page.
    window.history.replaceState(null, '', url)
  }, [])

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold sm:text-3xl">Buscar cartas</h1>
      <div className="grid gap-6 lg:grid-cols-[18rem_1fr] lg:items-start">
        <CardFilters
          filters={filters}
          onChange={(patch) => apply({ ...filters, ...patch, page: patch.page ?? 1 })}
          onReset={() => apply(EMPTY_FILTERS)}
        />
        <CardGrid
          state={state}
          page={filters.page}
          onPage={(page) => {
            apply({ ...filters, page })
            window.scrollTo({ top: 0 })
          }}
          onSelect={(card) => setSelectedId(card.id)}
        />
      </div>
      {selectedId && <CardDetail cardId={selectedId} onClose={() => setSelectedId(null)} />}
    </div>
  )
}
