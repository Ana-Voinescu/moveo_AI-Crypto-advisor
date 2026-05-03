import VoteButtons from '../shared/VoteButtons'
import './PriceCard.css'

function formatPrice(price) {
  return price.toLocaleString('en-US', { style: 'currency', currency: 'USD' })
}

function formatChange(change) {
  if (change == null) return null
  const sign = change >= 0 ? '+' : ''
  return `${sign}${change.toFixed(2)}%`
}

export default function PriceCard({ prices, votes }) {
  return (
    <div className="card dashboard-card">
      <h2 className="card-title">📈 Coin Prices</h2>

      <ul className="price-list">
        {prices.map(coin => (
          <li key={coin.symbol} className="price-row">
            <span className="coin-symbol">{coin.symbol}</span>
            <span className="coin-price">{formatPrice(coin.price_usd)}</span>
            {coin.change_24h != null && (
              <span className={coin.change_24h >= 0 ? 'positive' : 'negative'}>
                {formatChange(coin.change_24h)}
              </span>
            )}
          </li>
        ))}
      </ul>

      <VoteButtons contentType="price" contentId="daily-prices"
        initialVote={votes?.['price:daily-prices'] ?? null} />
    </div>
  )
}
