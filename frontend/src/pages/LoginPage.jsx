import { Link } from 'react-router-dom'
import LoginForm from '../components/auth/LoginForm'
import './AuthPage.css'

export default function LoginPage() {
  return (
    <div className="auth-page">
      <div className="auth-card card">
        <div className="auth-header">
          <div className="auth-logo">₿ Crypto Dashboard</div>
          <h2>Welcome back</h2>
          <p>Log in to see your personalised dashboard</p>
        </div>

        <LoginForm />

        <p className="auth-switch">
          Don't have an account? <Link to="/signup">Sign up</Link>
        </p>
      </div>
    </div>
  )
}
