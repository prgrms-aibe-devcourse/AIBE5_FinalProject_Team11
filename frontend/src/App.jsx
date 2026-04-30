import { useState } from 'react'
import ChatPanel from './components/ChatPanel'
import SearchPanel from './components/SearchPanel'
import MatchPanel from './components/MatchPanel'
import StudioChatPanel from './components/StudioChatPanel'
import JsonLd from './components/JsonLd'
import { buildFaqPageSchema, buildWebSiteSchema } from './schemas/faqSchema'

const TABS = [
  { id: 'chat',   label: 'Chat',   emoji: '🧘', desc: 'Ask Elbee anything about yoga matching & onboarding' },
  { id: 'search', label: 'Search', emoji: '🔍', desc: 'Search yoga content & knowledge base' },
  { id: 'match',  label: 'Match',  emoji: '✨', desc: 'Get personalised pose recommendations' },
  { id: 'studio', label: 'Studio', emoji: '🏢', desc: 'elbee Studio — operator chatbot for slots, weather, reviews & copy' },
]

const FAQ_SCHEMA    = buildFaqPageSchema()
const WEBSITE_SCHEMA = buildWebSiteSchema()

export default function App() {
  const [activeTab, setActiveTab] = useState('home')

  return (
    <div className="app">
      <JsonLd schema={FAQ_SCHEMA}     id="schema-faqpage" />
      <JsonLd schema={WEBSITE_SCHEMA} id="schema-website" />
      <header className="app-header">
        <div className="header-brand" onClick={() => setActiveTab('home')} style={{ cursor: 'pointer' }}>
          <span className="brand-icon">🧘</span>
          <div>
            <h1>Elbee Yoga Guide</h1>
            <p>Matching · Recommendations · Onboarding</p>
          </div>
        </div>
        {activeTab !== 'home' && (
          <nav className="tab-nav">
            <button
              className="tab-btn"
              onClick={() => setActiveTab('home')}
              title="Back to home"
            >
              ← Home
            </button>
            {TABS.map(tab => (
              <button
                key={tab.id}
                className={`tab-btn ${activeTab === tab.id ? 'active' : ''}`}
                onClick={() => setActiveTab(tab.id)}
                title={tab.desc}
              >
                {tab.emoji} {tab.label}
              </button>
            ))}
          </nav>
        )}
      </header>

      <main className="app-main">
        {activeTab === 'home' && (
          <section className="landing">
            <div className="landing-inner">
              <h2 className="landing-title">your yoga curator · 요가큐</h2>
              <p className="landing-tagline">
                AI-powered yoga matching, search, and operator tooling — built on the
                Elbee FYT100 pose library.
              </p>
              <p className="landing-about">
                <strong>Elbee Yoga Guide</strong> helps practitioners find poses that match
                their goals and health needs, while giving studio operators an
                AI assistant for scheduling, weather-aware exposure routing, review
                replies, and Korean marketing copy. Pick a workspace below to get started.
              </p>
              <div className="landing-grid">
                {TABS.map(tab => (
                  <button
                    key={tab.id}
                    className="landing-card"
                    onClick={() => setActiveTab(tab.id)}
                  >
                    <span className="landing-card-emoji">{tab.emoji}</span>
                    <span className="landing-card-label">{tab.label}</span>
                    <span className="landing-card-desc">{tab.desc}</span>
                  </button>
                ))}
              </div>
            </div>
          </section>
        )}
        {activeTab === 'chat'   && <ChatPanel />}
        {activeTab === 'search' && <SearchPanel />}
        {activeTab === 'match'  && <MatchPanel />}
        {activeTab === 'studio' && <StudioChatPanel />}
      </main>

      <footer className="app-footer">
        <span>Elbee Yoga Guide · FYT100 · yogaman.club</span>
        <span className="footer-links">
          <a href="/api/v1/poses" target="_blank" rel="noopener">Poses API</a>
          <a href="/chat/health" target="_blank" rel="noopener">Chat health</a>
          <a href="/studio/chat/health" target="_blank" rel="noopener">Studio health</a>
          <a href="/search/health" target="_blank" rel="noopener">Search health</a>
        </span>
      </footer>
    </div>
  )
}
