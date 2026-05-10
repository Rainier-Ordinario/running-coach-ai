import Sparkline from './Sparkline'

// Three sparklines: HRV, Sleep duration, Training Readiness.
function VitalsCard({ health }) {
  if (!health || health.length === 0) return null

  // Backend sends newest first; the Sparkline expects oldest → newest.
  const last7 = health.slice(0, 7).reverse()
  const hrv       = last7.map((d) => d.hrv).filter((v) => v != null)
  const sleep     = last7.map((d) => d.sleep).filter((v) => v != null)
  const readiness = last7.map((d) => d.readiness).filter((v) => v != null)

  const tail = (arr) => (arr.length ? arr[arr.length - 1] : '—')

  return (
    <div className="card vitals">
      <div className="card-head">
        <div className="card-title">Recovery vitals</div>
        <div className="card-eyebrow mono">last 7 days</div>
      </div>

      <div className="vitals-row">
        <div className="vitals-row-head">
          <span className="vitals-name">HRV</span>
          <span className="mono">
            {tail(hrv)}<span className="muted small"> ms</span>
          </span>
        </div>
        <Sparkline data={hrv} stroke="#8eb88a" fill="rgba(142,184,138,0.12)" height={32} />
      </div>

      <div className="vitals-row">
        <div className="vitals-row-head">
          <span className="vitals-name">Sleep</span>
          <span className="mono">
            {tail(sleep)}<span className="muted small"> h</span>
          </span>
        </div>
        <Sparkline data={sleep} stroke="#c5a373" fill="rgba(197,163,115,0.12)" height={32} />
      </div>

      <div className="vitals-row">
        <div className="vitals-row-head">
          <span className="vitals-name">Readiness</span>
          <span className="mono">
            {tail(readiness)}<span className="muted small"> /100</span>
          </span>
        </div>
        <Sparkline data={readiness} stroke="var(--accent)" fill="rgba(252,76,2,0.12)" height={32} />
      </div>
    </div>
  )
}

export default VitalsCard
