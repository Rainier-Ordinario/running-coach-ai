import { useState } from 'react'
import '../styles/SyncButton.css'

function SyncButton({ onSyncComplete }) {
  const [state, setState] = useState('default')
  const [count, setCount] = useState(0)

  const handleSync = async () => {
    setState('loading')

    try {
      const response = await fetch('/api/sync', { method: 'POST' })
      const data = await response.json()

      setCount(data.count)
      setState('success')

      setTimeout(() => setState('default'), 3000)
      onSyncComplete()
    } catch (error) {
      console.error('Sync failed:', error)
      setState('default')
    }
  }

  let text = 'Sync Strava'
  if (state === 'loading') text = 'Syncing...'
  if (state === 'success') text = `Synced ${count} runs ✓`

  return (
    <button
      onClick={handleSync}
      disabled={state === 'loading'}
      className={`sync-btn sync-${state}`}
    >
      {text}
    </button>
  )
}

export default SyncButton
