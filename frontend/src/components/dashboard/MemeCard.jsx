import { useState } from 'react'
import VoteButtons from '../shared/VoteButtons'
import './MemeCard.css'

export default function MemeCard({ meme, votes }) {
  const [imgError, setImgError] = useState(false)

  return (
    <div className="card dashboard-card">
      <h2 className="card-title">😂 Crypto Meme</h2>
      <p className="meme-title">{meme.title}</p>

      <div className="meme-media">
        {imgError ? (
          <div className="meme-fallback">Image could not be loaded</div>
        ) : (
          <img
            src={meme.url}
            alt={meme.title}
            className="meme-image"
            onError={() => setImgError(true)}
          />
        )}

        <VoteButtons contentType="meme" contentId={meme.id}
          initialVote={votes?.[`meme:${meme.id}`] ?? null} />
      </div>
    </div>
  )
}
