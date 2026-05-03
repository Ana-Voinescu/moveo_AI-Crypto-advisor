import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import * as api from '../../services/api'
import './AuthForm.css'

export default function SignupForm() {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const { loginUser } = useAuth()
  const navigate = useNavigate()

  async function handleSubmit(e) {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      const data = await api.signup(name, email, password)
      loginUser(data.token, data.user)
      // New users always go to onboarding first
      navigate('/onboarding')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
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
        <input
          id="password"
          type="password"
          value={password}
          onChange={e => setPassword(e.target.value)}
          placeholder="••••••••"
          required
          minLength={8}
        />
        <p className="field-hint">Min 8 characters, with uppercase, lowercase, and a number</p>
      </div>

      {error && <p className="error-message">{error}</p>}

      <button type="submit" className="btn btn-primary" disabled={loading}>
        {loading ? 'Creating account…' : 'Create account'}
      </button>
    </form>
  )
}
