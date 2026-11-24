// All calls to the SlotSaver backend go through this file.
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

async function request(path) {
  let res
  try {
    res = await fetch(`${API_URL}${path}`)
  } catch {
    throw new Error(`Cannot reach the API at ${API_URL}. Is the backend running?`)
  }
  const body = await res.json().catch(() => ({}))
  if (!res.ok) {
    const detail = Array.isArray(body.detail) ? body.detail.join('; ') : body.detail
    throw new Error(detail || `Request failed (${res.status})`)
  }
  return body
}

export const getHealth = () => request('/health')

export function getAppointments({ date, minRisk } = {}) {
  const params = new URLSearchParams()
  if (date) params.set('date', date)
  if (minRisk !== undefined && minRisk !== '') params.set('min_risk', minRisk)
  const qs = params.toString()
  return request(`/appointments${qs ? `?${qs}` : ''}`)
}
