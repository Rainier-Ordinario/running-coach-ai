import { useEffect, useState, useCallback } from 'react'
import { getStatus, getDashboard } from './api'
import Sidebar from './components/Sidebar'
import SyncButton from './components/SyncButton'
import Header from './components/Header'
import TodayStrip from './components/TodayStrip'
import CoachPanel from './components/CoachPanel'
import LastRunCard from './components/LastRunCard'
import VitalsCard from './components/VitalsCard'
import MileageChart from './components/MileageChart'
import RecentRuns from './components/RecentRuns'
import './styles/index.css'

function App() {
  const [status, setStatus] = useState(null)
  const [dashboard, setDashboard] = useState(null)
  const [error, setError] = useState(null)

  // Pull both /api/status and /api/dashboard. Status drives the empty-state UI;
  // dashboard provides everything the panels need to render.
  const refresh = useCallback(async () => {
    try {
      const s = await getStatus()
      setStatus(s)
      if (s.has_data) {
        const d = await getDashboard()
        setDashboard(d)
      } else {
        setDashboard(null)
      }
      setError(null)
    } catch (e) {
      console.error(e)
      setError(e.message)
    }
  }, [])

  useEffect(() => { refresh() }, [refresh])

  // Initial loading state — before the first /api/status returns.
  if (!status && !error) {
    return <div className="app-loading mono">Loading…</div>
  }

  // Empty state — no synced data yet. Trigger a sync from inside the card.
  if (!status?.has_data) {
    return (
      <div className="app-empty">
        <div className="app-empty-card">
          <h2>Sync your Garmin data</h2>
          <p>
            Pull your runs and recovery metrics from Garmin Connect to start
            getting AI-coached recommendations grounded in your actual numbers.
          </p>
          <SyncButton onSyncComplete={refresh} />
        </div>
      </div>
    )
  }

  const totals = dashboard?.totals
  const currentHealth = dashboard?.current_health
  const activities = dashboard?.activities || []
  const health = dashboard?.health || []
  const weeks = dashboard?.weekly_mileage || []
  const today = dashboard?.today
  const latestRace = activities.find((a) => a.tag === 'RACE') || null

  return (
    <div className="app-shell">
      <Sidebar syncedAt={status?.synced_at} onSyncComplete={refresh} />

      <main className="main">
        <Header today={today} totals={totals} />

        <TodayStrip
          today={today}
          currentHealth={currentHealth}
          latestRace={latestRace}
        />

        <div className="grid grid-3col">
          <CoachPanel readiness={currentHealth?.readiness} />
          <aside className="context-col">
            <LastRunCard activities={activities} />
            <VitalsCard health={health} />
          </aside>
        </div>

        <section className="grid grid-2col-balanced">
          <div className="card mileage-card">
            <div className="card-head">
              <div>
                <div className="card-eyebrow mono">Weekly mileage</div>
                <div className="card-title">Build → Peak → Taper → Race</div>
              </div>
              <div className="card-tag mono">last 14 weeks</div>
            </div>
            <MileageChart weeks={weeks} />
            <div className="mileage-legend mono small muted">
              <span><i className="dot dot-bar" /> kilometers</span>
              <span><i className="dot dot-current" /> current week</span>
            </div>
          </div>
          <RecentRuns activities={activities} />
        </section>
      </main>
    </div>
  )
}

export default App
