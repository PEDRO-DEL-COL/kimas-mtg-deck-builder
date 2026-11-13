import { useEffect, useState } from 'react'
import Footer from './components/Footer.tsx'
import Header from './components/Header.tsx'
import HomePage from './pages/HomePage.tsx'
import SearchPage from './pages/SearchPage.tsx'

function isSearchRoute(hash: string): boolean {
  return hash === '#/busca' || hash.startsWith('#/busca?')
}

function useHash(): string {
  const [hash, setHash] = useState(() => window.location.hash)
  useEffect(() => {
    const onChange = () => setHash(window.location.hash)
    window.addEventListener('hashchange', onChange)
    return () => window.removeEventListener('hashchange', onChange)
  }, [])
  return hash
}

export default function App() {
  const hash = useHash()
  const search = isSearchRoute(hash)

  return (
    <div className="flex min-h-screen flex-col">
      <Header searchActive={search} />
      <main className="mx-auto w-full max-w-7xl flex-1 px-4 py-10 sm:px-6">
        {search ? <SearchPage key={hash} /> : <HomePage />}
      </main>
      <Footer />
    </div>
  )
}
