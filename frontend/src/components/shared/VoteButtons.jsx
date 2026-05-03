import { useState } from 'react'
import * as api from '../../services/api'
import './VoteButtons.css'

export default function VoteButtons({ contentType, contentId, initialVote = null }) {
  const [voted, setVoted] = useState(initialVote)

  async function handleVote(value) {
    if (voted === value) return // clicking the same button twice does nothing
    try {
      await api.submitVote(contentType, contentId, value)
      setVoted(value)
    } catch (err) {
      console.error('Vote failed:', err)
    }
  }

  return (
    <div className="vote-buttons">
      <button
        className={`vote-btn ${voted === true ? 'vote-active-up' : ''}`}
        onClick={() => handleVote(true)}
        title="Helpful"
      >
        👍
      </button>
      <button
        className={`vote-btn ${voted === false ? 'vote-active-down' : ''}`}
        onClick={() => handleVote(false)}
        title="Not helpful"
      >
        👎
      </button>
    </div>
  )
}
