export default function Header() {
  return (
    <header className="border-b border-border bg-surface/80 backdrop-blur">
      <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-4 sm:px-6">
        <a href="/" className="text-lg font-bold text-text hover:text-primary-hover">
          Kima's <span className="text-primary">MTG</span> Deck Builder
        </a>
        <span className="rounded-full border border-border px-3 py-1 text-xs text-muted">
          Commander 10
        </span>
      </div>
    </header>
  )
}
