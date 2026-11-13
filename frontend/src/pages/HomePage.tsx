const features = [
  {
    title: 'Busca avançada',
    text: 'Filtre cartas por cor, tipo, custo de mana, texto e muito mais, usando os dados do Scryfall.',
  },
  {
    title: 'Deck builder',
    text: 'Monte seu deck de Commander com 100 cartas e acompanhe a lista em tempo real.',
  },
  {
    title: 'Orçamento Commander 10',
    text: 'Comandante até R$ 5,00 e demais cartas até R$ 10,00, com validação automática.',
  },
  {
    title: 'Preços do LigaMagic',
    text: 'Preços em reais coletados do LigaMagic, sempre com a data da coleta.',
  },
]

export default function HomePage() {
  return (
    <div className="space-y-12">
      <section className="space-y-4 text-center">
        <h1 className="text-3xl font-bold sm:text-5xl">Kima's MTG Deck Builder</h1>
        <p className="mx-auto max-w-2xl text-muted">
          Monte decks de Commander 10: um deck de 100 cartas em que o comandante custa até R$ 5,00 e
          as demais cartas custam até R$ 10,00 cada.
        </p>
        <form
          className="mx-auto flex max-w-xl flex-col gap-2 sm:flex-row"
          onSubmit={(e) => {
            e.preventDefault()
            const q = String(new FormData(e.currentTarget).get('q') ?? '').trim()
            window.location.hash = q ? `#/busca?q=${encodeURIComponent(q)}` : '#/busca'
          }}
        >
          <input
            type="search"
            name="q"
            placeholder="Buscar cartas pelo nome"
            aria-label="Buscar cartas pelo nome"
            className="flex-1 rounded-card border border-border bg-surface px-4 py-3 text-text placeholder:text-muted focus:border-primary focus:outline-none"
          />
          <button
            type="submit"
            className="rounded-card bg-primary px-5 py-3 font-semibold text-white shadow-card hover:bg-primary-hover"
          >
            Buscar
          </button>
        </form>
      </section>

      <section className="grid gap-4 sm:grid-cols-2">
        {features.map((f) => (
          <article
            key={f.title}
            className="rounded-card border border-border bg-surface p-5 shadow-card"
          >
            <h2 className="mb-2 text-lg font-semibold text-primary-hover">{f.title}</h2>
            <p className="text-sm text-muted">{f.text}</p>
          </article>
        ))}
      </section>
    </div>
  )
}
