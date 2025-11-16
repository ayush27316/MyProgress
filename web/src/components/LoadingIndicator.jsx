import { Loader2 } from 'lucide-react'
import './LoadingIndicator.css'

function LoadingIndicator() {
  return (
    <div className="loading-indicator">
      <div className="loading-content">
        <Loader2 className="loading-spinner" size={48} />
        <h3>Generating Audit Report</h3>
        <p>This may take up to 10 minutes. Please wait...</p>
        <div className="loading-progress">
          <div className="loading-bar"></div>
        </div>
      </div>
    </div>
  )
}

export default LoadingIndicator

