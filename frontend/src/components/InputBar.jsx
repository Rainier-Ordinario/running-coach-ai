import { useState } from 'react'
import '../styles/InputBar.css'

function InputBar({ onSendMessage, disabled }) {
  const [input, setInput] = useState('')

  const handleSubmit = () => {
    if (input.trim() && !disabled) {
      onSendMessage(input)
      setInput('')
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  return (
    <div className="input-bar">
      <textarea
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Ask me anything about your training..."
        disabled={disabled}
        rows="3"
      />
      <button
        onClick={handleSubmit}
        disabled={disabled || !input.trim()}
        className="send-btn"
      >
        Send
      </button>
    </div>
  )
}

export default InputBar
