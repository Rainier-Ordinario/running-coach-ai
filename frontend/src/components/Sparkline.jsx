// Tiny inline SVG line chart for the vitals card.
function Sparkline({ data, height = 36, stroke = 'var(--accent)', fill = 'rgba(252,76,2,0.10)' }) {
  if (!data || data.length === 0) return null

  const w = 200
  const h = height
  const pad = 2

  const min = Math.min(...data)
  const max = Math.max(...data)
  const range = max - min || 1
  const step = (w - pad * 2) / (data.length - 1 || 1)

  const points = data.map((v, i) => [
    pad + i * step,
    h - pad - ((v - min) / range) * (h - pad * 2),
  ])

  const path = points
    .map((p, i) => `${i === 0 ? 'M' : 'L'}${p[0].toFixed(1)},${p[1].toFixed(1)}`)
    .join(' ')

  // Close the area path back to the baseline so we can fill underneath the line.
  const fillPath = `${path} L${points[points.length - 1][0]},${h} L${points[0][0]},${h} Z`

  return (
    <svg
      viewBox={`0 0 ${w} ${h}`}
      preserveAspectRatio="none"
      style={{ width: '100%', height: h, display: 'block' }}
    >
      <path d={fillPath} fill={fill} />
      <path d={path} fill="none" stroke={stroke} strokeWidth="1.5" strokeLinejoin="round" strokeLinecap="round" />
    </svg>
  )
}

export default Sparkline
