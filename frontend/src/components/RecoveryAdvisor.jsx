import { useState } from 'react'
import '../styles/RecoveryAdvisor.css'

function RecoveryAdvisor() {
  const [recommendation, setRecommendation] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleGetRecommendation = async () => {
    setLoading(true)

    try {
      const response = await fetch('/api/recovery')
      const data = await response.json()
      setRecommendation(data.recommendation)
    } catch (error) {
      console.error('Recovery recommendation failed:', error)
      setRecommendation('Sorry, could not get recommendation. Make sure you have synced your Garmin data.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="recovery-advisor">
      <h2>Recovery Advisor</h2>
      <p>Check your current health metrics and get a rest vs train recommendation</p>

      <button
        onClick={handleGetRecommendation}
        disabled={loading}
        className="recovery-btn"
      >
        {loading ? 'Analyzing...' : 'Get Recommendation'}
      </button>

      {recommendation && (
        <div className="recommendation-box">
          {recommendation}
        </div>
      )}
    </div>
  )
}

export default RecoveryAdvisor
