// Thin wrappers over the backend. All routes are proxied to localhost:8000.

async function jsonOrThrow(res) {
  if (!res.ok) {
    const err = await res.text().catch(() => res.statusText)
    throw new Error(`${res.status}: ${err}`)
  }
  return res.json()
}

export function getStatus() {
  return fetch('/api/status').then(jsonOrThrow)
}

export function getDashboard() {
  return fetch('/api/dashboard').then(jsonOrThrow)
}

export function getProfile() {
  return fetch('/api/profile').then(jsonOrThrow)
}

export function postSync() {
  return fetch('/api/sync', { method: 'POST' }).then(jsonOrThrow)
}

export function postChat(question, history) {
  return fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, history }),
  }).then(jsonOrThrow)
}
