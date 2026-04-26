import { useState, useRef, useEffect, useCallback } from 'react'

const ONBOARDING_STARTERS = [
  'How does the yoga pose matching system work?',
  'What goals can I choose from when finding poses?',
  'How do I get pose recommendations for lower back pain?',
  'What is the difference between beginner and advanced poses?',
  'How do I start a yoga session with this app?',
  'What body focus areas can I target with the matching system?',
]

const INITIAL_MESSAGE = {
  role: 'assistant',
  content:
    "Hi! I'm Elbee, your yoga guide 🧘 I can explain how the matching and recommendation system works, help you find the right poses for your goals, and answer any questions about onboarding. What would you like to know?",
  sources: [],
  streaming: false,
}

export default function ChatPanel() {
  const [messages, setMessages]       = useState([INITIAL_MESSAGE])
  const [input, setInput]             = useState('')
  const [isStreaming, setIsStreaming]  = useState(false)
  const [statusLine, setStatusLine]   = useState('')
  const bottomRef                     = useRef(null)
  const inputRef                      = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, statusLine])

  const buildHistory = useCallback((msgs) =>
    msgs
      .filter(m => !m.streaming)
      .map(m => ({ role: m.role, content: m.content })),
  [])

  async function sendMessage(overrideText) {
    const question = (overrideText ?? input).trim()
    if (!question || isStreaming) return

    setInput('')
    setIsStreaming(true)
    setStatusLine('Connecting…')

    const history = buildHistory(messages)

    // Append user bubble
    setMessages(prev => [...prev, { role: 'user', content: question, sources: [] }])
    // Append empty assistant bubble that we'll fill via streaming
    setMessages(prev => [
      ...prev,
      { role: 'assistant', content: '', sources: [], streaming: true },
    ])

    try {
      const res = await fetch('/chat/stream', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question, history, stream: true }),
      })

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}: ${res.statusText}`)
      }

      const reader  = res.body.getReader()
      const decoder = new TextDecoder()
      let buffer    = ''
      let sources   = []

      // eslint-disable-next-line no-constant-condition
      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const parts = buffer.split('\n\n')
        buffer = parts.pop() // keep any incomplete last chunk

        for (const part of parts) {
          if (!part.startsWith('data: ')) continue
          let chunk
          try {
            chunk = JSON.parse(part.slice(6))
          } catch {
            continue
          }

          if (chunk.type === 'thinking') {
            setStatusLine(chunk.content)
          } else if (chunk.type === 'context') {
            try { sources = JSON.parse(chunk.content) } catch { sources = [] }
            setStatusLine(`Found ${sources.length} reference${sources.length !== 1 ? 's' : ''}…`)
          } else if (chunk.type === 'token') {
            setMessages(prev => {
              const updated = [...prev]
              const last    = { ...updated[updated.length - 1] }
              last.content  = (last.content || '') + chunk.content
              updated[updated.length - 1] = last
              return updated
            })
          } else if (chunk.type === 'done') {
            setMessages(prev => {
              const updated = [...prev]
              const last    = { ...updated[updated.length - 1] }
              last.streaming = false
              last.sources   = sources
              updated[updated.length - 1] = last
              return updated
            })
            setStatusLine('')
            setIsStreaming(false)
          } else if (chunk.type === 'error') {
            setMessages(prev => {
              const updated = [...prev]
              const last    = { ...updated[updated.length - 1] }
              last.content  = `⚠️ ${chunk.content}`
              last.streaming = false
              updated[updated.length - 1] = last
              return updated
            })
            setStatusLine('')
            setIsStreaming(false)
          }
        }
      }
    } catch (err) {
      setMessages(prev => {
        const updated = [...prev]
        const last    = { ...updated[updated.length - 1] }
        last.content  = `⚠️ Connection error: ${err.message}`
        last.streaming = false
        updated[updated.length - 1] = last
        return updated
      })
      setStatusLine('')
      setIsStreaming(false)
    } finally {
      // Ensure streaming flag is cleared if we somehow exit without setting it
      setIsStreaming(s => { if (s) return false; return s })
      inputRef.current?.focus()
    }
  }

  function handleKey(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const showStarters = messages.length === 1

  return (
    <div className="chat-panel">
      {/* Message list */}
      <div className="messages-area">
        {messages.map((msg, i) => (
          <div key={i} className={`message-row ${msg.role}`}>
            <div className="avatar">{msg.role === 'assistant' ? '🧘' : '🙋'}</div>
            <div className="bubble-wrap">
              <div className={`bubble ${msg.streaming ? 'streaming' : ''}`}>
                {msg.content
                  ? <span style={{ whiteSpace: 'pre-wrap' }}>{msg.content}</span>
                  : msg.streaming
                    ? <span className="cursor-blink">▋</span>
                    : null}
              </div>
              {msg.sources && msg.sources.length > 0 && (
                <div className="source-list">
                  {msg.sources.map((s, j) => (
                    <span key={j} className="source-badge">
                      📖 {s.book} p.{s.page}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {statusLine && (
          <div className="status-line">
            <span className="spinner" /> {statusLine}
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Onboarding starters — shown only while conversation is fresh */}
      {showStarters && (
        <div className="starters-section">
          <p className="starters-label">Onboarding questions to get you started:</p>
          <div className="starters-grid">
            {ONBOARDING_STARTERS.map((q, i) => (
              <button
                key={i}
                className="starter-btn"
                onClick={() => sendMessage(q)}
                disabled={isStreaming}
              >
                {q}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input row */}
      <form
        className="input-row"
        onSubmit={e => { e.preventDefault(); sendMessage() }}
      >
        <textarea
          ref={inputRef}
          className="chat-input"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKey}
          placeholder="Ask about yoga matching, onboarding, pose recommendations…"
          rows={2}
          disabled={isStreaming}
        />
        <button
          type="submit"
          className="send-btn"
          disabled={isStreaming || !input.trim()}
        >
          {isStreaming ? '⏳' : 'Send ↑'}
        </button>
      </form>
    </div>
  )
}
