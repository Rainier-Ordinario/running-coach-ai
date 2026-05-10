import { useEffect, useState, useCallback } from 'react'
import { getStatus, getDashboard, getProfile } from './api'
import Sidebar from './components/Sidebar'
import SyncButton from './components/SyncButton'
import Header from './components/Header'
import TodayStrip from './components/TodayStrip'
import CoachPanel from './components/CoachPanel'
import MileageChart from './components/MileageChart'
import RecentRuns from './components/RecentRuns'
import './styles/index.css'

function App() {
  const [status, setStatus] = useState(null)
  const [dashboard, setDashboard] = useState(null)
  const [profile, setProfile] = useState(null)
  const [error, setError] = useState(null)

  // Pull /api/status, then /api/dashboard + /api/profile in parallel when synced.
  // Status drives the empty-state UI and tells us whether profile is already cached
  // (a cache miss triggers a Garmin auth call so it can be slow on first run).
  const refresh = useCallback(async () => {
    try {
      const s = await getStatus()
      setStatus(s)

      if (!s.has_data) {
        setDashboard(null)
        setProfile(null)
        setError(null)
        return
      }

      const dashboardPromise = getDashboard()
      // Always try /api/profile when we have data; the endpoint will lazily fetch
      // and cache on first call. Swallow errors so the UI still renders.
      const profilePromise = getProfile().catch((e) => {
        console.warn('Profile fetch failed (falling back to placeholder):', e)
        return null
      })

      const [d, p] = await Promise.all([dashboardPromise, profilePromise])
      setDashboard(d)
      setProfile(p)
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
  const weeks = dashboard?.weekly_mileage || []
  const today = dashboard?.today
  const latestRace = activities.find((a) => a.tag === 'RACE') || null

  return (
    <div className="app-shell">
      <Sidebar
        syncedAt={status?.synced_at}
        onSyncComplete={refresh}
        profile={profile}
      />

      <main className="main">
        <Header today={today} totals={totals} firstName={profile?.first_name} />

        <TodayStrip
          today={today}
          currentHealth={currentHealth}
          latestRace={latestRace}
        />

        <CoachPanel readiness={currentHealth?.readiness} />

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
