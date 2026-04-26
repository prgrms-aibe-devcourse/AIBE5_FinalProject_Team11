import { useState } from 'react'
import ChatPanel from './components/ChatPanel'
import SearchPanel from './components/SearchPanel'
import MatchPanel from './components/MatchPanel'
import JsonLd from './components/JsonLd'
import { buildFaqPageSchema, buildWebSiteSchema } from './schemas/faqSchema'

const TABS = [
  { id: 'chat',   label: '🧘 Chat',   desc: 'Ask Elbee anything about yoga matching & onboarding' },
  { id: 'search', label: '🔍 Search', desc: 'Search yoga content & knowledge base' },
  { id: 'match',  label: '✨ Match',  desc: 'Get personalised pose recommendations' },
]

const FAQ_SCHEMA    = buildFaqPageSchema()
const WEBSITE_SCHEMA = buildWebSiteSchema()

export default function App() {
  const [activeTab, setActiveTab] = useState('chat')

  return (
    <div className="app">
      <JsonLd schema={FAQ_SCHEMA}     id="schema-faqpage" />
      <JsonLd schema={WEBSITE_SCHEMA} id="schema-website" />
      <header className="app-header">
        <div className="header-brand">
          <span className="brand-icon">🧘</span>
          <div>
            <h1>Elbee Yoga Guide</h1>
            <p>Matching · Recommendations · Onboarding</p>
          </div>
        </div>
        <nav className="tab-nav">
          {TABS.map(tab => (
            <button
              key={tab.id}
              className={`tab-btn ${activeTab === tab.id ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.id)}
              title={tab.desc}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </header>

      <main className="app-main">
        {activeTab === 'chat'   && <ChatPanel />}
        {activeTab === 'search' && <SearchPanel />}
        {activeTab === 'match'  && <MatchPanel />}
      </main>

      <footer className="app-footer">
        <span>Elbee Yoga Guide · FYT100 · yogaman.club</span>
        <span className="footer-links">
          <a href="/api/v1/poses" target="_blank" rel="noopener">Poses API</a>
          <a href="/chat/health" target="_blank" rel="noopener">Chat health</a>
          <a href="/search/health" target="_blank" rel="noopener">Search health</a>
        </span>
      </footer>
    </div>
  )
}
