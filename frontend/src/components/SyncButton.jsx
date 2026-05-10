import { useState } from 'react'
import { postSync } from '../api'

// Sync trigger styled to fit inside the sidebar's sync-card.
function SyncButton({ onSyncComplete }) {
  const [state, setState] = useState('default')
  const [count, setCount] = useState(0)

  const handleSync = async () => {
    setState('loading')
    try {
      const data = await postSync()
      setCount(data.count)
      setState('success')
      // Snap back to the default label after a short success window.
      setTimeout(() => setState('default'), 3000)
      if (onSyncComplete) onSyncComplete()
    } catch (e) {
      console.error('Sync failed:', e)
      setState('default')
    }
  }

  let label = 'Sync now'
  if (state === 'loading') label = 'Syncing…'
  if (state === 'success') label = `Synced ${count} ✓`

  return (
    <button onClick={handleSync} disabled={state === 'loading'} className="sync-btn mono">
      {label}
    </button>
  )
}

export default SyncButton
