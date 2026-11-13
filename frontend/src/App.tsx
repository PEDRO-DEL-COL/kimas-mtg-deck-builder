import Footer from './components/Footer.tsx'
import Header from './components/Header.tsx'
import HomePage from './pages/HomePage.tsx'

export default function App() {
  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      <main className="mx-auto w-full max-w-5xl flex-1 px-4 py-10 sm:px-6">
        <HomePage />
      </main>
      <Footer />
    </div>
  )
}
