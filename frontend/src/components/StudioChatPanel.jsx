import { useState, useRef, useEffect, useCallback } from 'react'

const STUDIO_STARTERS = [
  '이번 주 비 예보로 우리 매장 노출 영향 알려주세요.',
  '화요일 19시 인요가 슬롯 추가하면 노출이 얼마나 오르나요?',
  '강남역 30대 직장인 점심 회복요가 카피 한 줄 만들어주세요.',
  '후기 #12 (강사 친절했지만 매트가 낡음) 답글 초안 써주세요.',
  '성수동 주말 오전 비 오는 날 실내 클래스 추천 카피를 만들어주세요.',
  '어메니티 등록이 누락돼서 노출에 손해 보는 항목이 뭔가요?',
]

const INITIAL_MESSAGE = {
  role: 'assistant',
  content:
    "안녕하세요, 사장님! 🏢 elbee Studio 운영 도우미예요. 슬롯 운영, 날씨 라우팅 영향, 후기 답글 초안, 마케팅 카피 작성을 도와드려요. 어떤 운영 결정이 필요하세요?",
  sources: [],
  streaming: false,
}

export default function StudioChatPanel() {
  const [messages, setMessages]      = useState([INITIAL_MESSAGE])
  const [input, setInput]            = useState('')
  const [isStreaming, setIsStreaming] = useState(false)
  const [statusLine, setStatusLine]  = useState('')
  const bottomRef                    = useRef(null)
  const inputRef                     = useRef(null)

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
    setStatusLine('연결 중…')

    const history = buildHistory(messages)

    setMessages(prev => [...prev, { role: 'user', content: question, sources: [] }])
    setMessages(prev => [
      ...prev,
      { role: 'assistant', content: '', sources: [], streaming: true },
    ])

    try {
      const res = await fetch('/studio/chat/stream', {
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
        buffer = parts.pop()

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
            setStatusLine(`참고 ${sources.length}건 확인 중…`)
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
        last.content  = `⚠️ 연결 오류: ${err.message}`
        last.streaming = false
        updated[updated.length - 1] = last
        return updated
      })
      setStatusLine('')
      setIsStreaming(false)
    } finally {
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
    <div className="chat-panel studio-panel">
      <div className="messages-area">
        {messages.map((msg, i) => (
          <div key={i} className={`message-row ${msg.role}`}>
            <div className="avatar">{msg.role === 'assistant' ? '🏢' : '👤'}</div>
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

      {showStarters && (
        <div className="starters-section">
          <p className="starters-label">운영자 자주 묻는 요청:</p>
          <div className="starters-grid">
            {STUDIO_STARTERS.map((q, i) => (
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
          placeholder="슬롯·노출·후기 답글·카피 등 운영 질문을 입력하세요…"
          rows={2}
          disabled={isStreaming}
        />
        <button
          type="submit"
          className="send-btn"
          disabled={isStreaming || !input.trim()}
        >
          {isStreaming ? '⏳' : '전송 ↑'}
        </button>
      </form>
    </div>
  )
}
