const linkClass = 'text-primary-hover underline-offset-2 hover:underline'

export default function Footer() {
  return (
    <footer className="border-t border-border bg-surface">
      <div className="mx-auto max-w-5xl space-y-2 px-4 py-6 text-sm text-muted sm:px-6">
        <p>
          Dados e imagens de cartas fornecidos pelo{' '}
          <a className={linkClass} href="https://scryfall.com" target="_blank" rel="noreferrer">
            Scryfall
          </a>
          . Preços fornecidos pelo{' '}
          <a
            className={linkClass}
            href="https://www.ligamagic.com.br"
            target="_blank"
            rel="noreferrer"
          >
            LigaMagic
          </a>
          .
        </p>
        <p>
          Este site não é afiliado à Wizards of the Coast. Conteúdo de fã não oficial (Unofficial
          Fan Content). Magic: The Gathering é marca registrada da Wizards of the Coast.
        </p>
        <p>
          <a
            className={linkClass}
            href="https://github.com/PEDRO-DEL-COL/kimas-mtg-deck-builder"
            target="_blank"
            rel="noreferrer"
          >
            Código no GitHub
          </a>{' '}
          · Licença AGPL-3.0
        </p>
      </div>
    </footer>
  )
}
