import { fmtPace, fmtDuration } from '../format'

// Highlights the latest race if there is one, otherwise the most recent run.
function LastRunCard({ activities }) {
  if (!activities || activities.length === 0) return null
  const last = activities.find((a) => a.tag === 'RACE') || activities[0]
  const isRace = last.tag === 'RACE'

  const stats = [
    { label: 'distance', value: last.km.toFixed(2), unit: 'km' },
    { label: 'time',     value: fmtDuration(last.sec), unit: '' },
    { label: 'pace',     value: fmtPace(last.km, last.sec), unit: '/km' },
    { label: 'avg hr',   value: last.hr ?? '—', unit: 'bpm' },
    { label: 'elev',     value: last.elev ?? 0, unit: 'm' },
    { label: 'load',     value: Math.round(last.load || 0), unit: '' },
  ]

  return (
    <div className="card last-run">
      <div className="card-head">
        <div>
          <div className="card-eyebrow mono">{isRace ? 'Latest race' : 'Latest run'}</div>
          <div className="card-title">{last.name}</div>
        </div>
        <div className="card-tag mono">{last.date}</div>
      </div>

      <div className="last-run-stats">
        {stats.map((s) => (
          <div key={s.label} className="last-run-stat">
            <div className="mono small muted">{s.label}</div>
            <div className="last-run-stat-value mono">
              {s.value}
              <span className="last-run-stat-unit">{s.unit}</span>
            </div>
          </div>
        ))}
      </div>

      <div className="last-run-zones">
        <div className="zones-label mono">aerobic</div>
        <div className="zones-bar">
          <div className="zones-fill" style={{ width: `${Math.min(100, ((last.te_aero || 0) / 5) * 100)}%` }} />
        </div>
        <div className="zones-value mono">{(last.te_aero || 0).toFixed(1)}</div>
      </div>
      <div className="last-run-zones">
        <div className="zones-label mono">anaerobic</div>
        <div className="zones-bar">
          <div className="zones-fill anaerobic" style={{ width: `${Math.min(100, ((last.te_anaero || 0) / 5) * 100)}%` }} />
        </div>
        <div className="zones-value mono">{(last.te_anaero || 0).toFixed(1)}</div>
      </div>
    </div>
  )
}

export default LastRunCard
