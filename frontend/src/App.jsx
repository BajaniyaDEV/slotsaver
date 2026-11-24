import { useEffect, useState } from 'react'
import { getHealth } from './api'
import Board from './Board'

// Screens are added here as they are built (Appointment detail, Ask SlotSaver, Waitlist, Model insights).
export default function App() {
  const [health, setHealth] = useState(null)

  useEffect(() => {
    getHealth()
      .then(setHealth)
      .catch(() => setHealth({ status: 'down' }))
  }, [])

  const dot =
    health?.status === 'ok' ? 'bg-emerald-500' : health?.status === 'degraded' ? 'bg-amber-500' : 'bg-red-500'

  return (
    <div className="min-h-screen text-slate-800">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <div>
            <h1 className="text-xl font-semibold">SlotSaver</h1>
            <p className="text-sm text-slate-500">No-show prediction and waitlist filling</p>
          </div>
          <div className="flex items-center gap-2 text-sm text-slate-500" title="API health">
            <span className={`h-2.5 w-2.5 rounded-full ${health ? dot : 'bg-slate-300'}`} />
            API {health ? health.status : 'checking…'}
          </div>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-6 py-6">
        <Board />
      </main>
    </div>
  )
}
