import '../styles/MessageBubble.css'

function MessageBubble({ role, content }) {
  const isUser = role === 'user'

  return (
    <div className={`bubble bubble-${role}`}>
      {content === null ? (
        <div className="loading-indicator">
          <span></span>
          <span></span>
          <span></span>
        </div>
      ) : (
        <p>{content}</p>
      )}
    </div>
  )
}

export default MessageBubble
