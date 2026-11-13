interface Props {
  searchActive: boolean
}

export default function Header({ searchActive }: Props) {
  const link = (active: boolean) =>
    `rounded-card px-3 py-1.5 text-sm ${active ? 'bg-background text-text' : 'text-muted hover:text-text'}`

  return (
    <header className="border-b border-border bg-surface/80 backdrop-blur">
      <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-2 px-4 py-4 sm:px-6">
        <a href="#/" className="text-lg font-bold text-text hover:text-primary-hover">
          Kima's <span className="text-primary">MTG</span> Deck Builder
        </a>
        <nav aria-label="Principal" className="flex items-center gap-1">
          <a
            href="#/"
            className={link(!searchActive)}
            aria-current={searchActive ? undefined : 'page'}
          >
            Início
          </a>
          <a
            href="#/busca"
            className={link(searchActive)}
            aria-current={searchActive ? 'page' : undefined}
          >
            Buscar cartas
          </a>
          <span className="ml-2 hidden rounded-full border border-border px-3 py-1 text-xs text-muted sm:inline">
            Commander 10
          </span>
        </nav>
      </div>
    </header>
  )
}
