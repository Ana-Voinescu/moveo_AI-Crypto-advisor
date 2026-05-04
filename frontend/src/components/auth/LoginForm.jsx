import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import * as api from '../../services/api'
import './AuthForm.css'

export default function LoginForm() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [slowWarning, setSlowWarning] = useState(false)
  const [error, setError] = useState(null)
  const timerRef = useRef(null)

  const { loginUser } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    if (loading) {
      timerRef.current = setTimeout(() => setSlowWarning(true), 4000)
    } else {
      clearTimeout(timerRef.current)
      setSlowWarning(false)
    }
    return () => clearTimeout(timerRef.current)
  }, [loading])

  async function handleSubmit(e) {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      const data = await api.login(email, password)
      loginUser(data.token, data.user)
      // Existing users who already completed onboarding go straight to the dashboard
      navigate(data.user.is_onboarded ? '/dashboard' : '/onboarding')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <form className="auth-form" onSubmit={handleSubmit}>
      <div className="form-group">
        <label htmlFor="email">Email</label>
        <input
          id="email"
          type="email"
          value={email}
          onChange={e => setEmail(e.target.value)}
          placeholder="you@example.com"
          required
        />
      </div>

      <div className="form-group">
        <label htmlFor="password">Password</label>
        <input
          id="password"
          type="password"
          value={password}
          onChange={e => setPassword(e.target.value)}
          placeholder="••••••••"
          required
        />
      </div>

      {error && <p className="error-message">{error}</p>}
      {slowWarning && (
        <p className="slow-warning">
          The server is waking up from sleep — this can take up to a minute on first load. Hang tight…
        </p>
      )}

      <button type="submit" className="btn btn-primary" disabled={loading}>
        {loading ? 'Logging in…' : 'Log in'}
      </button>
    </form>
  )
}
