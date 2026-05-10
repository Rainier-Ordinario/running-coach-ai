// 14-week mileage bars. Last bar is the current week and gets a brighter fill.
function MileageChart({ weeks }) {
  if (!weeks || weeks.length === 0) return null
  const max = Math.max(...weeks.map((w) => w.km), 1)

  return (
    <div className="mileage-chart">
      <div className="mileage-bars">
        {weeks.map((w, i) => {
          const isCurrent = i === weeks.length - 1
          // 140px is the bar track height defined in styles. Keep at least 2px so empty weeks stay visible.
          const h = Math.max(2, (w.km / max) * 140)
          return (
            <div key={w.wk} className="mileage-col" title={`${w.wk}: ${w.km.toFixed(1)} km`}>
              <div className="mileage-bar-track">
                <div
                  className={`mileage-bar ${isCurrent ? 'is-current' : ''}`}
                  style={{ height: `${h}px` }}
                />
              </div>
              <div className="mileage-bar-label mono">{w.km.toFixed(0)}</div>
              <div className="mileage-bar-week mono">{w.wk.slice(5)}</div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default MileageChart
