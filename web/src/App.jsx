import { useState } from 'react'
import TranscriptBuilder from './components/TranscriptBuilder'
import ReportViewer from './components/ReportViewer'
import LoadingIndicator from './components/LoadingIndicator'
import './App.css'

function App() {
  const [reports, setReports] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const [transcriptCollapsed, setTranscriptCollapsed] = useState(false)

  const handleAudit = async (transcriptData) => {
    setLoading(true)
    setError(null)
    setReports(null)

    try {
      const response = await fetch('/audit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(transcriptData),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      setReports(data.reports)
      setTranscriptCollapsed(true) // Collapse transcript builder after successful audit
    } catch (err) {
      setError(err.message)
      console.error('Error generating audit:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <main className="app-main">
        <div className="app-container">
          <div className="app-logo">myProgress-ultra-pro-max</div>
          
          <div className="app-container-content">
            {!transcriptCollapsed && (
              <div className="app-section">
                <TranscriptBuilder 
                  onAudit={handleAudit} 
                  loading={loading}
                  onCollapse={() => setTranscriptCollapsed(true)}
                />
              </div>
            )}

            {transcriptCollapsed && (
              <div className="app-section">
                <button 
                  className="btn-expand-transcript"
                  onClick={() => setTranscriptCollapsed(false)}
                >
                  Show Transcript Builder
                </button>
              </div>
            )}

            {loading && (
              <div className="app-section">
                <LoadingIndicator />
              </div>
            )}

            {error && (
              <div className="error-message">
                <strong>Error:</strong> {error}
              </div>
            )}

            {reports && !loading && (
              <div className="app-section">
                <ReportViewer reports={reports} />
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}

export default App

