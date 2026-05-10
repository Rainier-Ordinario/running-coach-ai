import { useState, useEffect, useRef } from 'react'
import { postChat } from '../api'

const SUGGESTED_PROMPTS = [
  'Should I run today, or rest?',
  'How did the marathon compare to my training?',
  'What was my biggest training mistake going into the race?',
  'When can I start hard intervals again?',
]

const STORAGE_KEY = 'runnercoach.chat.v1'

// Light markdown rendering: paragraphs, dash bullets, **bold**.
function FormattedContent({ text }) {
  const lines = text.split(/\n+/)
  return (
    <div className="msg-content">
      {lines.map((line, i) => {
        const t = line.trim()
        if (!t) return null
        if (/^[-•*]\s+/.test(t)) {
          return (
            <div key={i} className="msg-bullet">
              · <span>{t.replace(/^[-•*]\s+/, '')}</span>
            </div>
          )
        }
        const parts = t.split(/(\*\*[^*]+\*\*)/g)
        return (
          <p key={i}>
            {parts.map((p, j) =>
              p.startsWith('**') && p.endsWith('**')
                ? <strong key={j}>{p.slice(2, -2)}</strong>
                : <span key={j}>{p}</span>,
            )}
          </p>
        )
      })}
    </div>
  )
}

function Message({ role, content }) {
  const isUser = role === 'user'
  return (
    <div className={`msg msg-${role}`}>
      <div className="msg-avatar mono">{isUser ? 'you' : 'coach'}</div>
      <div className="msg-bubble">
        {content === null
          ? <span className="dots"><span /><span /><span /></span>
          : <FormattedContent text={content} />}
      </div>
    </div>
  )
}

function CoachPanel({ readiness }) {
  // Persist chat history across reloads so the conversation feels continuous.
  const [messages, setMessages] = useState(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY)
      if (raw) return JSON.parse(raw)
    } catch (_e) { /* ignore */ }
    return []
  })
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const scrollRef = useRef(null)

  useEffect(() => {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(messages)) } catch (_e) { /* ignore */ }
    if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight
  }, [messages, loading])

  const ask = async (question) => {
    if (!question.trim() || loading) return
    const next = [...messages, { role: 'user', content: question }]
    setMessages(next)
    setInput('')
    setLoading(true)

    try {
      // Backend expects 'role' values it understands ('user' | 'coach') in the history.
      const data = await postChat(question, messages)
      setMessages((prev) => [...prev, { role: 'coach', content: data.answer }])
    } catch (e) {
      console.error(e)
      setMessages((prev) => [
        ...prev,
        { role: 'coach', content: "Sorry — couldn't reach the coach just now. Try again in a moment." },
      ])
    } finally {
      setLoading(false)
    }
  }

  const onSubmit = (e) => { e.preventDefault(); ask(input) }
  const onKey = (e) => {
    // Enter sends; Shift+Enter inserts a newline.
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      ask(input)
    }
  }
  const clear = () => {
    setMessages([])
    try { localStorage.removeItem(STORAGE_KEY) } catch (_e) { /* ignore */ }
  }

  return (
    <section className="coach">
      <div className="coach-head">
        <div>
          <div className="card-eyebrow mono">AI Coach</div>
          <h2 className="coach-title">Ask anything about your training.</h2>
          <div className="coach-sub">Grounded in your last 80 runs and 30 days of recovery data.</div>
        </div>
        <div className="coach-head-right">
          <span className="status-dot" />
          <span className="mono small muted">claude · live</span>
          {messages.length > 0 && (
            <button onClick={clear} className="coach-clear mono">clear</button>
          )}
        </div>
      </div>

      <div className="coach-body" ref={scrollRef}>
        {messages.length === 0 && !loading && (
          <div className="coach-empty">
            <div className="mono small muted">Try asking</div>
            <div className="prompt-grid">
              {SUGGESTED_PROMPTS.map((p) => (
                <button key={p} className="prompt-chip" onClick={() => ask(p)}>
                  <span className="prompt-chip-arrow">→</span>
                  <span>{p}</span>
                </button>
              ))}
            </div>
            <div className="coach-empty-context">
              <div className="mono small muted">The coach is reading</div>
              <ul className="context-list mono small">
                <li>· last 80 runs (incl. recent races)</li>
                <li>· 30-day HRV, sleep, stress, body battery</li>
                {readiness != null && <li>· today's training readiness ({readiness}/100)</li>}
              </ul>
            </div>
          </div>
        )}

        {messages.map((m, i) => (
          <Message key={i} role={m.role} content={m.content} />
        ))}

        {loading && <Message role="coach" content={null} />}
      </div>

      <form className="coach-input" onSubmit={onSubmit}>
        <textarea
          rows={1}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={onKey}
          placeholder={loading ? 'Coach is thinking…' : 'Ask about training, recovery, pacing, plans…'}
          disabled={loading}
        />
        <button type="submit" disabled={loading || !input.trim()} className="coach-send">
          {loading
            ? <span className="dots"><span /><span /><span /></span>
            : 'Ask coach'}
        </button>
      </form>
    </section>
  )
}

export default CoachPanel
