import { useState, useEffect } from 'react'
import Chat from './components/Chat'
import InputBar from './components/InputBar'
import SyncButton from './components/SyncButton'
import './styles/index.css'

function App() {
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)
  const [synced, setSynced] = useState(false)

  // Check if activity data is available on mount
  useEffect(() => {
    const checkStatus = async () => {
      try {
        const response = await fetch('/api/status')
        const data = await response.json()
        setSynced(data.has_data)
      } catch (error) {
        console.error('Status check failed:', error)
      }
    }

    checkStatus()
  }, [])

  const handleSyncComplete = () => {
    setSynced(true)
  }

  // Send message to coach and wait for response
  const handleSendMessage = async (question) => {
    setMessages((prev) => [...prev, { role: 'user', content: question }])
    setLoading(true)

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question,
          history: messages,
        }),
      })

      const data = await response.json()
      setMessages((prev) => [...prev, { role: 'coach', content: data.answer }])
    } catch (error) {
      console.error('Chat failed:', error)
      setMessages((prev) => [
        ...prev,
        { role: 'coach', content: 'Sorry, something went wrong.' },
      ])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <div className="header">
        <h1>Marathon AI Coach</h1>
        <SyncButton onSyncComplete={handleSyncComplete} />
      </div>

      {!synced ? (
        <div className="empty-state">
          <p>Sync your Strava data to get started</p>
        </div>
      ) : (
        <>
          <Chat messages={messages} loading={loading} />
          <InputBar
            onSendMessage={handleSendMessage}
            disabled={loading}
          />
        </>
      )}
    </div>
  )
}

export default App
