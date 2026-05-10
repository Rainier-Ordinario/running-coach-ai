import { fmtPrettyDate } from '../format'

// Greeting eyebrow + 7d / YTD / runs stats. Cmd-K is decorative for now.
function Header({ today, totals, firstName, eyebrowSuffix }) {
  const eyebrow = `${fmtPrettyDate(today)}${eyebrowSuffix ? ` · ${eyebrowSuffix}` : ''}`
  // While the profile is in flight, show a neutral placeholder.
  const greeting = firstName ? `Welcome back, ${firstName}.` : 'Welcome back, Athlete.'

  return (
    <header className="header">
      <div>
        <div className="hello-eyebrow mono">{eyebrow}</div>
        <h1 className="hello">{greeting}</h1>
      </div>

      <div className="header-stats">
        <div className="header-stat">
          <div className="mono x-small muted">7d</div>
          <div className="mono header-stat-value">
            {(totals?.last7_distance_km ?? 0).toFixed(1)}
            <span className="header-stat-unit">km</span>
          </div>
        </div>
        <div className="header-stat">
          <div className="mono x-small muted">YTD</div>
          <div className="mono header-stat-value">
            {Math.round(totals?.ytd_distance_km ?? 0)}
            <span className="header-stat-unit">km</span>
          </div>
        </div>
        <div className="header-stat">
          <div className="mono x-small muted">runs</div>
          <div className="mono header-stat-value">{totals?.ytd_runs ?? 0}</div>
        </div>
        <button className="cmd-btn mono">⌘ K</button>
      </div>
    </header>
  )
}

export default Header
