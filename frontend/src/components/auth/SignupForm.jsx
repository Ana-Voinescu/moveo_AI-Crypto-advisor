import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import * as api from '../../services/api'
import PageLoader from '../shared/PageLoader'
import './AuthForm.css'

export default function SignupForm() {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
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
    if (password !== confirmPassword) {
      setError('Passwords do not match.')
      return
    }
    setError(null)
    setLoading(true)
    try {
      const data = await api.signup(name, email, password)
      loginUser(data.token, data.user)
      navigate('/onboarding')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      {loading && <PageLoader />}
      <form className="auth-form" onSubmit={handleSubmit}>
      <div className="form-group">
        <label htmlFor="name">Name</label>
        <input
          id="name"
          type="text"
          value={name}
          onChange={e => setName(e.target.value)}
          placeholder="Your name"
          required
        />
      </div>

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
        <div className="input-with-toggle">
          <input
            id="password"
            type={showPassword ? 'text' : 'password'}
            value={password}
            onChange={e => setPassword(e.target.value)}
            placeholder="••••••••"
            required
            minLength={8}
          />
          <button type="button" className="eye-toggle" onClick={() => setShowPassword(v => !v)}>
            {showPassword ? '🙈' : '👁️'}
          </button>
        </div>
        <p className="field-hint">Min 8 characters, with uppercase, lowercase, and a number</p>
      </div>

      <div className="form-group">
        <label htmlFor="confirmPassword">Confirm Password</label>
        <div className="input-with-toggle">
          <input
            id="confirmPassword"
            type={showPassword ? 'text' : 'password'}
            value={confirmPassword}
            onChange={e => setConfirmPassword(e.target.value)}
            placeholder="••••••••"
            required
          />
          <button type="button" className="eye-toggle" onClick={() => setShowPassword(v => !v)}>
            {showPassword ? '🙈' : '👁️'}
          </button>
        </div>
      </div>

      {error && <p className="error-message">{error}</p>}
      {slowWarning && (
        <p className="slow-warning">
          The server is waking up from sleep — this can take up to a minute on first load. Hang tight…
        </p>
      )}

      <button type="submit" className="btn btn-primary" disabled={loading}>
        {loading ? 'Creating account…' : 'Create account'}
      </button>
    </form>
    </>
  )
}
