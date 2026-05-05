import './LoadingSpinner.css'

export default function LoadingSpinner({ message = 'Loading...' }) {
  return (
    <div className="spinner-wrapper">
      <div className="dots-loader">
        <span className="dot" />
        <span className="dot" />
        <span className="dot" />
      </div>
      <p className="spinner-message">{message}</p>
    </div>
  )
}
