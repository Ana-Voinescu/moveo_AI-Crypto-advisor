import OnboardingForm from '../components/onboarding/OnboardingForm'
import './OnboardingPage.css'

export default function OnboardingPage() {
  return (
    <div className="onboarding-page">
      <div className="onboarding-card card">
        <div className="onboarding-header">
          <div className="auth-logo">₿ Crypto Dashboard</div>
          <h2>Tell us about yourself</h2>
          <p>We'll use your answers to personalise your daily dashboard</p>
        </div>
        <OnboardingForm />
      </div>
    </div>
  )
}
