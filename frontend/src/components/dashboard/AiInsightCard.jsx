import VoteButtons from '../shared/VoteButtons'
import './AiInsightCard.css'

export default function AiInsightCard({ insight, votes }) {
  return (
    <div className="card dashboard-card">
      <h2 className="card-title">🤖 AI Insight of the Day</h2>
      <blockquote className="insight-text">{insight}</blockquote>
      <VoteButtons contentType="ai_insight" contentId="daily"
        initialVote={votes?.['ai_insight:daily'] ?? null} />
    </div>
  )
}
