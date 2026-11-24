import { useEffect, useState } from 'react'
import { getAppointments } from './api'

function tomorrowISO() {
  const d = new Date()
  d.setDate(d.getDate() + 1)
  const pad = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
}

const BAND_STYLES = {
  high: 'bg-red-100 text-red-800 ring-red-200',
  medium: 'bg-amber-100 text-amber-800 ring-amber-200',
  low: 'bg-emerald-100 text-emerald-800 ring-emerald-200',
}

function RiskBadge({ score, band }) {
  if (score === null || score === undefined) {
    return <span className="text-xs text-slate-400">Not scored yet</span>
  }
  return (
    <span className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium ring-1 ${BAND_STYLES[band] || ''}`}>
      {band} · {Math.round(score * 100)}%
    </span>
  )
}

export default function Board() {
  const [date, setDate] = useState(tomorrowISO())
  const [minRisk, setMinRisk] = useState('')
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    setLoading(true)
    setError('')
    getAppointments({ date, minRisk })
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [date, minRisk])

  const placeholder = data?.appointments.some((a) => a.risk_score !== null)

  return (
    <section>
      <div className="mb-4 rounded-lg border border-sky-200 bg-sky-50 px-4 py-3 text-sm text-sky-900">
        Risk scores are used only to plan reminders and extra support, never to refuse or overbook care.
        Staff approve every action.
      </div>

      <div className="mb-4 flex flex-wrap items-end justify-between gap-4">
        <div>
          <h2 className="text-lg font-semibold">Tomorrow's board</h2>
          <p className="text-sm text-slate-500">
            {data ? `${data.count} appointments` : ' '} · highest risk first
          </p>
        </div>
        <div className="flex gap-3">
          <label className="text-sm">
            <span className="mb-1 block text-slate-500">Date</span>
            <input
              type="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
              className="rounded-md border border-slate-300 bg-white px-2 py-1.5"
            />
          </label>
          <label className="text-sm">
            <span className="mb-1 block text-slate-500">Show</span>
            <select
              value={minRisk}
              onChange={(e) => setMinRisk(e.target.value)}
              className="rounded-md border border-slate-300 bg-white px-2 py-1.5"
            >
              <option value="">All appointments</option>
              <option value="0.2">Medium and high risk</option>
              <option value="0.4">High risk only</option>
            </select>
          </label>
        </div>
      </div>

      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">{error}</div>
      )}

      {loading && !error && <p className="py-8 text-center text-slate-500">Loading appointments…</p>}

      {!loading && !error && data?.count === 0 && (
        <p className="py-8 text-center text-slate-500">No appointments for this date and filter.</p>
      )}

      {!loading && !error && data?.count > 0 && (
        <div className="overflow-x-auto rounded-lg border border-slate-200 bg-white">
          <table className="min-w-full text-sm">
            <thead className="bg-slate-50 text-left text-slate-500">
              <tr>
                <th className="px-4 py-2 font-medium">Time</th>
                <th className="px-4 py-2 font-medium">Patient</th>
                <th className="px-4 py-2 font-medium">Language</th>
                <th className="px-4 py-2 font-medium">Visit</th>
                <th className="px-4 py-2 font-medium">Provider</th>
                <th className="px-4 py-2 font-medium">Booked</th>
                <th className="px-4 py-2 font-medium">Risk</th>
                <th className="px-4 py-2 font-medium">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {data.appointments.map((a) => (
                <tr key={a.id} className="hover:bg-slate-50">
                  <td className="px-4 py-2 whitespace-nowrap">
                    {new Date(a.appointment_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </td>
                  <td className="px-4 py-2">{a.patient_name}</td>
                  <td className="px-4 py-2">{a.preferred_language}</td>
                  <td className="px-4 py-2">{a.visit_type}</td>
                  <td className="px-4 py-2">{a.provider}</td>
                  <td className="px-4 py-2 text-slate-500">{a.lead_days === 0 ? 'Same day' : `${a.lead_days} days ahead`}</td>
                  <td className="px-4 py-2">
                    <RiskBadge score={a.risk_score} band={a.risk_band} />
                  </td>
                  <td className="px-4 py-2 capitalize">{a.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {placeholder && (
        <p className="mt-3 text-xs text-slate-400">
          Scores shown may be placeholders from the seed script until the trained model is connected.
        </p>
      )}
    </section>
  )
}
