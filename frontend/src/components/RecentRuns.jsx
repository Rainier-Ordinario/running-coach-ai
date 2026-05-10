import { fmtPace } from '../format'

const ROWS_TO_SHOW = 8

function RecentRuns({ activities }) {
  const runs = (activities || []).slice(0, ROWS_TO_SHOW)
  const total = activities ? activities.length : 0

  return (
    <div className="card recent-runs">
      <div className="card-head">
        <div className="card-title">Recent runs</div>
        <div className="card-eyebrow mono">{runs.length} of {total}</div>
      </div>
      <div className="recent-runs-list">
        {runs.map((r, i) => (
          <div key={`${r.date}-${i}`} className="run-row">
            <div className="run-date mono">{r.date.slice(5)}</div>
            <div className="run-name">
              {r.name}
              {r.tag && <span className="run-tag mono">{r.tag}</span>}
            </div>
            <div className="run-km mono">
              {r.km.toFixed(1)}<span className="run-km-unit">km</span>
            </div>
            <div className="run-pace mono muted">{fmtPace(r.km, r.sec)}/km</div>
            <div className="run-hr mono muted">
              {r.hr ?? '—'}<span className="small"> bpm</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default RecentRuns
