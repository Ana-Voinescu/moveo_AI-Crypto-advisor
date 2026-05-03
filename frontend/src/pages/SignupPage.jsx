import { Link } from 'react-router-dom'
import SignupForm from '../components/auth/SignupForm'
import './AuthPage.css'

export default function SignupPage() {
  return (
    <div className="auth-page">
      <div className="auth-card card">
        <div className="auth-header">
          <div className="auth-logo">₿ Crypto Dashboard</div>
          <h2>Create your account</h2>
          <p>Answer a short quiz to personalise your feed</p>
        </div>

        <SignupForm />

        <p className="auth-switch">
          Already have an account? <Link to="/login">Log in</Link>
        </p>
      </div>
    </div>
  )
}
