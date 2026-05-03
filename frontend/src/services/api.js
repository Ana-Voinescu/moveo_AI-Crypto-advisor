const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function getAuthHeaders() {
  const token = localStorage.getItem('token')
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  }
}

async function request(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, options)
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error(body.detail || 'Something went wrong')
  }
  return res.json()
}

export function signup(name, email, password) {
  return request('/api/auth/signup', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, email, password }),
  })
}

export function login(email, password) {
  return request('/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  })
}

export function saveOnboarding(crypto_assets, investor_type, content_types) {
  return request('/api/onboarding', {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({ crypto_assets, investor_type, content_types }),
  })
}

export function getDashboard() {
  return request('/api/dashboard', {
    headers: getAuthHeaders(),
  })
}

export function submitVote(content_type, content_id, vote) {
  return request('/api/vote', {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({ content_type, content_id, vote }),
  })
}
