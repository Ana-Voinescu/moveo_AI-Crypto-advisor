import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import * as api from '../../services/api'
import './OnboardingForm.css'

const COINS = ['BTC', 'ETH', 'SOL', 'ADA', 'DOGE', 'DOT', 'AVAX', 'XRP']

const INVESTOR_TYPES = [
  { value: 'hodler',        label: 'HODLer',        desc: 'I buy and hold long-term' },
  { value: 'day_trader',    label: 'Day Trader',    desc: 'I actively trade the markets' },
  { value: 'nft_collector', label: 'NFT Collector', desc: 'I focus on digital collectibles' },
]

const CONTENT_TYPES = [
  { value: 'news',   label: 'Market News' },
  { value: 'charts', label: 'Charts' },
  { value: 'social', label: 'Social' },
  { value: 'fun',    label: 'Fun & Memes' },
]

export default function OnboardingForm() {
  const [selectedCoins, setSelectedCoins]     = useState([])
  const [investorType, setInvestorType]       = useState('')
  const [selectedContent, setSelectedContent] = useState([])
  const [loading, setLoading]                 = useState(false)
  const [error, setError]                     = useState(null)
  const navigate = useNavigate()

  function toggleCoin(coin) {
    setSelectedCoins(prev =>
      prev.includes(coin) ? prev.filter(c => c !== coin) : [...prev, coin]
    )
  }

  function toggleContent(type) {
    setSelectedContent(prev =>
      prev.includes(type) ? prev.filter(t => t !== type) : [...prev, type]
    )
  }

  async function handleSubmit(e) {
    e.preventDefault()
    if (selectedCoins.length === 0) return setError('Please select at least one coin.')
    if (!investorType)              return setError('Please select your investor type.')
    if (selectedContent.length === 0) return setError('Please select at least one content type.')

    setError(null)
    setLoading(true)
    try {
      await api.saveOnboarding(selectedCoins, investorType, selectedContent)
      navigate('/dashboard')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <form className="onboarding-form" onSubmit={handleSubmit}>

      {/* Section 1: Coins */}
      <div className="onboarding-section">
        <h3>Which crypto assets interest you?</h3>
        <p className="section-hint">Select one or more</p>
        <div className="chip-grid">
          {COINS.map(coin => (
            <button
              key={coin}
              type="button"
              className={`chip ${selectedCoins.includes(coin) ? 'chip-selected' : ''}`}
              onClick={() => toggleCoin(coin)}
            >
              {coin}
            </button>
          ))}
        </div>
      </div>

      {/* Section 2: Investor type */}
      <div className="onboarding-section">
        <h3>What type of investor are you?</h3>
        <div className="investor-grid">
          {INVESTOR_TYPES.map(({ value, label, desc }) => (
            <label
              key={value}
              className={`investor-card ${investorType === value ? 'investor-card-selected' : ''}`}
            >
              <input
                type="radio"
                name="investorType"
                value={value}
                checked={investorType === value}
                onChange={() => setInvestorType(value)}
              />
              <span className="investor-label">{label}</span>
              <span className="investor-desc">{desc}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Section 3: Content types */}
      <div className="onboarding-section">
        <h3>What content would you like to see?</h3>
        <p className="section-hint">Select one or more</p>
        <div className="chip-grid">
          {CONTENT_TYPES.map(({ value, label }) => (
            <button
              key={value}
              type="button"
              className={`chip ${selectedContent.includes(value) ? 'chip-selected' : ''}`}
              onClick={() => toggleContent(value)}
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      {error && <p className="error-message">{error}</p>}

      <button type="submit" className="btn btn-primary" disabled={loading}>
        {loading ? 'Saving…' : 'Go to my dashboard →'}
      </button>

    </form>
  )
}
