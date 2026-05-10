import SyncButton from './SyncButton'

// Static placeholder nav — only "Dashboard" is implemented.
const NAV_ITEMS = [
  { icon: '▮', label: 'Dashboard', active: true },
  { icon: '▷', label: 'Activities' },
  { icon: '◇', label: 'Plan' },
  { icon: '◑', label: 'Recovery' },
  { icon: '◧', label: 'Records' },
  { icon: '◔', label: 'Coach' },
]

function fmtSyncedAt(iso) {
  if (!iso) return 'Not synced yet'
  // Trim trailing "+00:00" / "Z" for compactness; show date · HH:MM UTC.
  const d = new Date(iso)
  if (isNaN(d)) return iso
  const date = d.toISOString().slice(0, 10)
  const time = d.toISOString().slice(11, 16)
  return `${date} · ${time} UTC`
}

// "Rainier Ordinario" -> "RO"; single-name -> first letter; nothing -> "—".
function deriveInitials(profile) {
  const full = profile?.full_name?.trim()
  if (!full) return '—'
  const parts = full.split(/\s+/).filter(Boolean)
  if (parts.length === 1) return parts[0][0].toUpperCase()
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase()
}

function Sidebar({ syncedAt, onSyncComplete, profile }) {
  const displayName = profile?.first_name || profile?.full_name || 'Athlete'
  const initials = deriveInitials(profile)
  return (
    <nav className="sidebar">
      <div className="brand">
        <div className="brand-mark" />
        <div className="brand-text">
          <div className="brand-name">Strider</div>
          <div className="brand-sub mono">marathon coach</div>
        </div>
      </div>

      <div className="nav-list">
        {NAV_ITEMS.map((it) => (
          <a key={it.label} className={`nav-item ${it.active ? 'active' : ''}`} href="#">
            <span className="nav-icon mono">{it.icon}</span>
            <span>{it.label}</span>
          </a>
        ))}
      </div>

      <div className="sidebar-foot">
        <div className="sync-card">
          <div className="sync-row">
            <span className={`status-dot ${syncedAt ? '' : 'is-muted'}`} />
            <span className="mono small">{syncedAt ? 'Garmin synced' : 'Not synced'}</span>
          </div>
          <div className="mono x-small muted">{fmtSyncedAt(syncedAt)}</div>
          <SyncButton onSyncComplete={onSyncComplete} />
        </div>
        <div className="profile">
          <div className="profile-avatar mono">{initials}</div>
          <div>
            <div className="profile-name">{displayName}</div>
            <div className="profile-sub mono">marathoner</div>
          </div>
        </div>
      </div>
    </nav>
  )
}

export default Sidebar
