// Display formatters shared across the dashboard components.

export function fmtPace(km, sec) {
  if (!km || !sec) return '—'
  const paceMin = (sec / 60) / km
  const minutes = Math.floor(paceMin)
  const seconds = Math.round((paceMin - minutes) * 60)
  const ss = seconds === 60 ? '00' : String(seconds).padStart(2, '0')
  return `${seconds === 60 ? minutes + 1 : minutes}:${ss}`
}

export function fmtDuration(sec) {
  if (!sec) return '0:00'
  const h = Math.floor(sec / 3600)
  const m = Math.floor((sec % 3600) / 60)
  const s = sec % 60
  if (h > 0) return `${h}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
  return `${m}:${String(s).padStart(2, '0')}`
}

const WEEKDAYS = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

export function fmtPrettyDate(isoDate) {
  if (!isoDate) return ''
  const [y, m, d] = isoDate.split('-').map(Number)
  // Construct in local time; the date is just a calendar day.
  const date = new Date(y, m - 1, d)
  return `${WEEKDAYS[date.getDay()]}, ${MONTHS[date.getMonth()]} ${date.getDate()}`
}

export function daysSince(isoDate, today) {
  if (!isoDate || !today) return null
  const a = new Date(isoDate)
  const b = new Date(today)
  return Math.round((b - a) / (1000 * 60 * 60 * 24))
}
