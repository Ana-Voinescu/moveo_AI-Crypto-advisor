import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import { AuthProvider } from '../context/AuthContext'
import DashboardPage from '../pages/DashboardPage'
import * as api from '../services/api'

vi.mock('../services/api')

const MOCK_DASHBOARD = {
  prices: [
    { symbol: 'BTC', price_usd: 50000, change_24h: 2.5 },
    { symbol: 'ETH', price_usd: 3000,  change_24h: -1.2 },
  ],
  ai_insight: 'BTC is showing strong bullish momentum.',
  news: [
    { id: '1', title: 'Bitcoin reaches new high', url: 'https://example.com/1', source: 'CoinDesk' },
  ],
  meme: { id: 'meme1', title: 'When BTC dips 1%', url: 'https://example.com/meme.jpg' },
  votes: {},
}

function renderDashboard() {
  localStorage.setItem('user', JSON.stringify({ id: 1, name: 'Alice', is_onboarded: true }))
  localStorage.setItem('token', 'test-token')

  return render(
    <MemoryRouter initialEntries={['/dashboard']}>
      <AuthProvider>
        <Routes>
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/login" element={<div>Login page</div>} />
        </Routes>
      </AuthProvider>
    </MemoryRouter>
  )
}

describe('DashboardPage', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.clearAllMocks()
  })

  test('shows loading message while fetching', () => {
    api.getDashboard.mockImplementation(() => new Promise(() => {}))
    renderDashboard()
    expect(screen.getByText('Loading your dashboard…')).toBeInTheDocument()
  })

  test('renders all 4 section headings after successful fetch', async () => {
    api.getDashboard.mockResolvedValue(MOCK_DASHBOARD)
    renderDashboard()

    await waitFor(() => {
      expect(screen.getByText('📈 Coin Prices')).toBeInTheDocument()
      expect(screen.getByText('🤖 AI Insight of the Day')).toBeInTheDocument()
      expect(screen.getByText('📰 Market News')).toBeInTheDocument()
      expect(screen.getByText('😂 Crypto Meme')).toBeInTheDocument()
    })
  })

  test('renders content from each section', async () => {
    api.getDashboard.mockResolvedValue(MOCK_DASHBOARD)
    renderDashboard()

    await waitFor(() => screen.getByText('BTC'))
    expect(screen.getByText('BTC is showing strong bullish momentum.')).toBeInTheDocument()
    expect(screen.getByText('Bitcoin reaches new high')).toBeInTheDocument()
    expect(screen.getByText('When BTC dips 1%')).toBeInTheDocument()
  })

  test('shows error message when fetch fails with a retry button', async () => {
    api.getDashboard.mockRejectedValue(new Error('Network error'))
    renderDashboard()

    await waitFor(() => expect(screen.getByText(/could not load dashboard/i)).toBeInTheDocument())
    expect(screen.getByRole('button', { name: /try again/i })).toBeInTheDocument()
  })

  test('retry button re-fetches the dashboard', async () => {
    api.getDashboard
      .mockRejectedValueOnce(new Error('Network error'))
      .mockResolvedValue(MOCK_DASHBOARD)

    renderDashboard()

    await waitFor(() => screen.getByRole('button', { name: /try again/i }))
    screen.getByRole('button', { name: /try again/i }).click()

    await waitFor(() => expect(screen.getByText('📈 Coin Prices')).toBeInTheDocument())
    expect(api.getDashboard).toHaveBeenCalledTimes(2)
  })
})
