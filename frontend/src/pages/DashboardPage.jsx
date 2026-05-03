import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import * as api from '../services/api'
import PriceCard from '../components/dashboard/PriceCard'
import NewsCard from '../components/dashboard/NewsCard'
import AiInsightCard from '../components/dashboard/AiInsightCard'
import MemeCard from '../components/dashboard/MemeCard'
import LoadingSpinner from '../components/shared/LoadingSpinner'
import './DashboardPage.css'

export default function DashboardPage() {
  const [data, setData]       = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError]     = useState(null)

  const { user, logoutUser } = useAuth()
  const navigate = useNavigate()

  async function loadDashboard() {
    setLoading(true)
    setError(null)
    try {
      const result = await api.getDashboard()
      setData(result)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadDashboard()
  }, [])

  function handleLogout() {
    logoutUser()
    navigate('/login')
  }

  return (
    <div className="dashboard-page">
      <header className="dashboard-header">
        <div className="header-brand">₿ Crypto Dashboard</div>
        <div className="header-right">
          <span className="header-greeting">Hello, {user?.name}</span>
          <button className="btn btn-ghost" onClick={handleLogout}>Log out</button>
        </div>
      </header>

      <main className="dashboard-main">
        {loading && <LoadingSpinner message="Loading your dashboard…" />}

        {error && !loading && (
          <div className="dashboard-error card">
            <p>Could not load dashboard: {error}</p>
            <button
              className="btn btn-primary"
              onClick={loadDashboard}
              style={{ width: 'auto', marginTop: '1rem' }}
            >
              Try again
            </button>
          </div>
        )}

        {data && !loading && (
          <div className="dashboard-grid">
            <PriceCard     prices={data.prices}     votes={data.votes} />
            <AiInsightCard insight={data.ai_insight} votes={data.votes} />
            <NewsCard      news={data.news}          votes={data.votes} />
            <MemeCard      meme={data.meme}          votes={data.votes} />
          </div>
        )}
      </main>
    </div>
  )
}
