import { daysSince } from '../format'

// Map readiness score → headline + tone. >=70 ready, <40 rest, otherwise recovering.
function statusFromReadiness(readiness) {
  if (readiness == null) return { label: 'NO DATA', tone: 'neutral' }
  if (readiness >= 70) return { label: 'READY', tone: 'good' }
  if (readiness < 40) return { label: 'REST', tone: 'warn' }
  return { label: 'RECOVERING', tone: 'neutral' }
}

function buildSubtext(latestRace, today) {
  if (!latestRace) {
    return 'Keep building base fitness with mostly easy aerobic running. Add intensity once readiness sits above 70.'
  }
  const days = daysSince(latestRace.date, today)
  if (days == null) return ''
  if (days <= 7) {
    return `${days} day${days === 1 ? '' : 's'} post-${latestRace.name.toLowerCase().includes('marathon') ? 'marathon' : 'race'}. Body Battery still rebuilding — easy aerobic only this week, no intensity until HRV settles.`
  }
  if (days <= 21) {
    return `${days} days post-race. You're in the recovery block — short easy runs and strides only.`
  }
  return 'Back into a build block — sessions can stack as long as readiness and HRV cooperate.'
}

function TodayStrip({ today, currentHealth, latestRace }) {
  const status = statusFromReadiness(currentHealth?.readiness)

  // HRV delta vs the prior reading day (if we have one).
  // Backend sends most recent first, so we compare current to the second day.
  const metrics = [
    {
      label: 'Training readiness',
      value: currentHealth?.readiness ?? '—',
      unit: '/100',
      note: currentHealth?.level || null,
    },
    {
      label: 'HRV',
      value: currentHealth?.hrv ?? '—',
      unit: 'ms',
    },
    {
      label: 'Body Battery',
      value: currentHealth?.bb ?? '—',
      unit: '/100',
    },
    {
      label: 'Sleep',
      value: currentHealth?.sleep ?? '—',
      unit: 'h',
      note: currentHealth?.sleep_q != null ? `score ${currentHealth.sleep_q}` : null,
    },
    {
      label: 'Resting HR',
      value: currentHealth?.rhr ?? '—',
      unit: 'bpm',
    },
    {
      label: 'Recovery',
      value: currentHealth?.recovery_h ?? '—',
      unit: 'h',
    },
  ]

  return (
    <section className="today-strip">
      <div className={`today-status today-status-${status.tone}`}>
        <div className="today-status-eyebrow mono">Today · {today}</div>
        <div className="today-status-headline">{status.label}</div>
        <div className="today-status-sub">{buildSubtext(latestRace, today)}</div>
        {latestRace && (
          <div className="today-status-tags mono">
            <span>Latest race: {latestRace.name}</span>
          </div>
        )}
      </div>
      <div className="today-metrics">
        {metrics.map((m) => (
          <div key={m.label} className="today-metric">
            <div className="today-metric-label mono">{m.label}</div>
            <div className="today-metric-value mono">
              {m.value}
              <span className="today-metric-unit">{m.unit}</span>
            </div>
            {m.note && <div className="today-metric-note mono">{m.note}</div>}
          </div>
        ))}
      </div>
    </section>
  )
}

export default TodayStrip
