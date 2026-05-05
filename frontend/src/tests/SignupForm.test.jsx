import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import { AuthProvider } from '../context/AuthContext'
import SignupForm from '../components/auth/SignupForm'
import * as api from '../services/api'

vi.mock('../services/api')

function renderSignup() {
  return render(
    <MemoryRouter initialEntries={['/signup']}>
      <AuthProvider>
        <Routes>
          <Route path="/signup" element={<SignupForm />} />
          <Route path="/onboarding" element={<div>Onboarding page</div>} />
        </Routes>
      </AuthProvider>
    </MemoryRouter>
  )
}

describe('SignupForm', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.clearAllMocks()
  })

  test('successful signup saves token and redirects to /onboarding', async () => {
    api.signup.mockResolvedValue({
      token: 'new-token',
      user: { id: 3, name: 'Carol', email: 'carol@example.com', is_onboarded: false },
    })

    renderSignup()
    fireEvent.change(screen.getByLabelText('Name'), { target: { value: 'Carol' } })
    fireEvent.change(screen.getByLabelText('Email'), { target: { value: 'carol@example.com' } })
    fireEvent.change(screen.getByLabelText('Password'), { target: { value: 'password123' } })
    fireEvent.change(screen.getByLabelText('Confirm Password'), { target: { value: 'password123' } })
    fireEvent.click(screen.getByRole('button', { name: /create account/i }))

    await waitFor(() => expect(screen.getByText('Onboarding page')).toBeInTheDocument())
    expect(localStorage.getItem('token')).toBe('new-token')
  })

  test('duplicate email error is displayed', async () => {
    api.signup.mockRejectedValue(new Error('Email already registered'))

    renderSignup()
    fireEvent.change(screen.getByLabelText('Name'), { target: { value: 'Dave' } })
    fireEvent.change(screen.getByLabelText('Email'), { target: { value: 'existing@example.com' } })
    fireEvent.change(screen.getByLabelText('Password'), { target: { value: 'password123' } })
    fireEvent.change(screen.getByLabelText('Confirm Password'), { target: { value: 'password123' } })
    fireEvent.click(screen.getByRole('button', { name: /create account/i }))

    await waitFor(() => expect(screen.getByText('Email already registered')).toBeInTheDocument())
  })

  test('shows loading state while request is in flight', async () => {
    api.signup.mockImplementation(() => new Promise(() => {}))

    renderSignup()
    fireEvent.change(screen.getByLabelText('Name'), { target: { value: 'Eve' } })
    fireEvent.change(screen.getByLabelText('Email'), { target: { value: 'eve@example.com' } })
    fireEvent.change(screen.getByLabelText('Password'), { target: { value: 'password123' } })
    fireEvent.change(screen.getByLabelText('Confirm Password'), { target: { value: 'password123' } })
    fireEvent.click(screen.getByRole('button', { name: /create account/i }))

    expect(screen.getByRole('button', { name: /creating account/i })).toBeDisabled()
  })

  test('shows error when passwords do not match', () => {
    renderSignup()
    fireEvent.change(screen.getByLabelText('Name'), { target: { value: 'Frank' } })
    fireEvent.change(screen.getByLabelText('Email'), { target: { value: 'frank@example.com' } })
    fireEvent.change(screen.getByLabelText('Password'), { target: { value: 'password123' } })
    fireEvent.change(screen.getByLabelText('Confirm Password'), { target: { value: 'different' } })
    fireEvent.click(screen.getByRole('button', { name: /create account/i }))

    expect(screen.getByText('Passwords do not match.')).toBeInTheDocument()
    expect(api.signup).not.toHaveBeenCalled()
  })
})
