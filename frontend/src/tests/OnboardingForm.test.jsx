import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import { AuthProvider } from '../context/AuthContext'
import OnboardingForm from '../components/onboarding/OnboardingForm'
import * as api from '../services/api'

vi.mock('../services/api')

function renderOnboarding() {
  return render(
    <MemoryRouter initialEntries={['/onboarding']}>
      <AuthProvider>
        <Routes>
          <Route path="/onboarding" element={<OnboardingForm />} />
          <Route path="/dashboard" element={<div>Dashboard page</div>} />
        </Routes>
      </AuthProvider>
    </MemoryRouter>
  )
}

describe('OnboardingForm', () => {
  beforeEach(() => vi.clearAllMocks())

  test('submitting a complete form calls the API and redirects to /dashboard', async () => {
    api.saveOnboarding.mockResolvedValue({})
    renderOnboarding()

    fireEvent.click(screen.getByRole('button', { name: 'BTC' }))
    fireEvent.click(screen.getByRole('radio', { name: /hodler/i }))
    fireEvent.click(screen.getByRole('button', { name: 'Market News' }))
    fireEvent.click(screen.getByRole('button', { name: /go to my dashboard/i }))

    await waitFor(() => expect(screen.getByText('Dashboard page')).toBeInTheDocument())
    expect(api.saveOnboarding).toHaveBeenCalledWith(['BTC'], 'hodler', ['news'])
  })

  test('shows validation error when no coin is selected', () => {
    renderOnboarding()
    fireEvent.click(screen.getByRole('button', { name: /go to my dashboard/i }))
    expect(screen.getByText('Please select at least one coin.')).toBeInTheDocument()
  })

  test('shows validation error when no investor type is selected', () => {
    renderOnboarding()
    fireEvent.click(screen.getByRole('button', { name: 'BTC' }))
    fireEvent.click(screen.getByRole('button', { name: /go to my dashboard/i }))
    expect(screen.getByText('Please select your investor type.')).toBeInTheDocument()
  })

  test('shows validation error when no content type is selected', () => {
    renderOnboarding()
    fireEvent.click(screen.getByRole('button', { name: 'BTC' }))
    fireEvent.click(screen.getByRole('radio', { name: /hodler/i }))
    fireEvent.click(screen.getByRole('button', { name: /go to my dashboard/i }))
    expect(screen.getByText('Please select at least one content type.')).toBeInTheDocument()
  })

  test('shows API error on failure', async () => {
    api.saveOnboarding.mockRejectedValue(new Error('Server error'))
    renderOnboarding()

    fireEvent.click(screen.getByRole('button', { name: 'BTC' }))
    fireEvent.click(screen.getByRole('radio', { name: /hodler/i }))
    fireEvent.click(screen.getByRole('button', { name: 'Market News' }))
    fireEvent.click(screen.getByRole('button', { name: /go to my dashboard/i }))

    await waitFor(() => expect(screen.getByText('Server error')).toBeInTheDocument())
  })
})
