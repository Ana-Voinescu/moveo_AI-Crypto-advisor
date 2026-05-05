import './PageLoader.css'

export default function PageLoader() {
  return (
    <div className="page-loader-overlay">
      <div className="dots-loader">
        <span className="dot" />
        <span className="dot" />
        <span className="dot" />
      </div>
    </div>
  )
}
