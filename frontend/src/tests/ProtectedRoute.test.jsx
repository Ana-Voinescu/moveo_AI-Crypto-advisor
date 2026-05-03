import { render, screen } from '@testing-library/react'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import { AuthProvider } from '../context/AuthContext'
import ProtectedRoute from '../components/shared/ProtectedRoute'

function renderWithAuth(isLoggedIn) {
  if (isLoggedIn) {
    localStorage.setItem('user', JSON.stringify({ id: 1, name: 'Alice' }))
    localStorage.setItem('token', 'test-token')
  }

  return render(
    <MemoryRouter initialEntries={['/dashboard']}>
      <AuthProvider>
        <Routes>
          <Route path="/dashboard" element={
            <ProtectedRoute><div>Dashboard content</div></ProtectedRoute>
          } />
          <Route path="/login" element={<div>Login page</div>} />
        </Routes>
      </AuthProvider>
    </MemoryRouter>
  )
}

describe('ProtectedRoute', () => {
  afterEach(() => localStorage.clear())

  test('unauthenticated user is redirected to /login', () => {
    renderWithAuth(false)
    expect(screen.getByText('Login page')).toBeInTheDocument()
    expect(screen.queryByText('Dashboard content')).not.toBeInTheDocument()
  })

  test('authenticated user sees the protected content', () => {
    renderWithAuth(true)
    expect(screen.getByText('Dashboard content')).toBeInTheDocument()
    expect(screen.queryByText('Login page')).not.toBeInTheDocument()
  })
})
