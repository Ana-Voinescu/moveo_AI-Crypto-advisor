import VoteButtons from '../shared/VoteButtons'
import './NewsCard.css'

export default function NewsCard({ news, votes }) {
  return (
    <div className="card dashboard-card">
      <h2 className="card-title">📰 Market News</h2>

      <ul className="news-list">
        {news.map(article => (
          <li key={article.id} className="news-item">
            <div className="news-content">
              <a
                href={article.url}
                target="_blank"
                rel="noopener noreferrer"
                className="news-title"
              >
                {article.title}
              </a>
              <span className="news-source">{article.source}</span>
            </div>
            <VoteButtons contentType="news" contentId={article.id}
              initialVote={votes?.[`news:${article.id}`] ?? null} />
          </li>
        ))}
      </ul>
    </div>
  )
}
