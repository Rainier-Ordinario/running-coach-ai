import { useEffect, useRef } from 'react'
import MessageBubble from './MessageBubble'

function Chat({ messages, loading }) {
  const scrollRef = useRef(null)

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages, loading])

  return (
    <div className="chat" ref={scrollRef}>
      {messages.length === 0 && !loading ? (
        <div className="chat-placeholder">Ask me anything about your training</div>
      ) : (
        messages.map((msg, i) => (
          <MessageBubble key={i} role={msg.role} content={msg.content} />
        ))
      )}
      {loading && <MessageBubble role="coach" content={null} />}
    </div>
  )
}

export default Chat
