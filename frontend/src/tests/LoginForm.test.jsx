import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import { AuthProvider } from '../context/AuthContext'
import LoginForm from '../components/auth/LoginForm'
import * as api from '../services/api'

vi.mock('../services/api')

function renderLogin() {
  return render(
    <MemoryRouter initialEntries={['/login']}>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginForm />} />
          <Route path="/dashboard" element={<div>Dashboard page</div>} />
          <Route path="/onboarding" element={<div>Onboarding page</div>} />
        </Routes>
      </AuthProvider>
    </MemoryRouter>
  )
}

describe('LoginForm', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.clearAllMocks()
  })

  test('successful login for onboarded user redirects to /dashboard', async () => {
    api.login.mockResolvedValue({
      token: 'test-token',
      user: { id: 1, name: 'Alice', email: 'alice@example.com', is_onboarded: true },
    })

    renderLogin()
    fireEvent.change(screen.getByLabelText('Email'), { target: { value: 'alice@example.com' } })
    fireEvent.change(screen.getByLabelText('Password'), { target: { value: 'password123' } })
    fireEvent.click(screen.getByRole('button', { name: /log in/i }))

    await waitFor(() => expect(screen.getByText('Dashboard page')).toBeInTheDocument())
    expect(localStorage.getItem('token')).toBe('test-token')
  })

  test('successful login for non-onboarded user redirects to /onboarding', async () => {
    api.login.mockResolvedValue({
      token: 'test-token',
      user: { id: 2, name: 'Bob', email: 'bob@example.com', is_onboarded: false },
    })

    renderLogin()
    fireEvent.change(screen.getByLabelText('Email'), { target: { value: 'bob@example.com' } })
    fireEvent.change(screen.getByLabelText('Password'), { target: { value: 'password123' } })
    fireEvent.click(screen.getByRole('button', { name: /log in/i }))

    await waitFor(() => expect(screen.getByText('Onboarding page')).toBeInTheDocument())
  })

  test('failed login displays the backend error message', async () => {
    api.login.mockRejectedValue(new Error('Invalid credentials'))

    renderLogin()
    fireEvent.change(screen.getByLabelText('Email'), { target: { value: 'alice@example.com' } })
    fireEvent.change(screen.getByLabelText('Password'), { target: { value: 'wrongpassword' } })
    fireEvent.click(screen.getByRole('button', { name: /log in/i }))

    await waitFor(() => expect(screen.getByText('Invalid credentials')).toBeInTheDocument())
  })

  test('shows loading state while request is in flight', async () => {
    api.login.mockImplementation(() => new Promise(() => {}))

    renderLogin()
    fireEvent.change(screen.getByLabelText('Email'), { target: { value: 'alice@example.com' } })
    fireEvent.change(screen.getByLabelText('Password'), { target: { value: 'password123' } })
    fireEvent.click(screen.getByRole('button', { name: /log in/i }))

    expect(screen.getByRole('button', { name: /logging in/i })).toBeDisabled()
  })
})
