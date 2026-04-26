import { useState } from 'react'

const SUGGESTED_SEARCHES = [
  'mountain pose benefits',
  'yoga for back pain',
  'beginner standing poses',
  'hip opening poses',
  'stress relief sequence',
]

export default function SearchPanel() {
  const [query,   setQuery]   = useState('')
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error,   setError]   = useState('')

  async function doSearch(overrideQuery) {
    const q = (overrideQuery ?? query).trim()
    if (!q) return

    setQuery(q)
    setLoading(true)
    setError('')
    setResults(null)

    try {
      const res = await fetch('/search', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ q }),
      })
      if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText}`)
      const data = await res.json()
      setResults(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const hits = results?.hits ?? results?.results ?? []

  return (
    <div className="search-panel">
      <div className="search-header">
        <h2>Knowledge Base Search</h2>
        <p>Search yoga content, GEO strategy, and onboarding documentation</p>
      </div>

      <form
        className="search-form"
        onSubmit={e => { e.preventDefault(); doSearch() }}
      >
        <input
          type="text"
          className="search-input"
          value={query}
          onChange={e => setQuery(e.target.value)}
          placeholder="Search yoga content…"
        />
        <button type="submit" className="search-btn" disabled={loading || !query.trim()}>
          {loading ? '⏳' : '🔍 Search'}
        </button>
      </form>

      {/* Suggested searches */}
      {!results && !loading && (
        <div className="suggested-searches">
          <p className="starters-label">Try searching for:</p>
          <div className="starters-grid">
            {SUGGESTED_SEARCHES.map((s, i) => (
              <button
                key={i}
                className="starter-btn"
                onClick={() => doSearch(s)}
              >
                {s}
              </button>
            ))}
          </div>
        </div>
      )}

      {error && (
        <div className="error-banner">
          ⚠️ {error}
        </div>
      )}

      {/* Results */}
      {hits.length > 0 && (
        <div className="search-results">
          <p className="results-count">{hits.length} result{hits.length !== 1 ? 's' : ''}</p>
          {hits.map((h, i) => (
            <div key={i} className="result-card">
              <div className="result-meta">
                <span className="result-book">📖 {h.book}</span>
                <span className="result-page">p.{h.page}</span>
                {h.score !== undefined && (
                  <span className="result-score">score: {h.score}</span>
                )}
              </div>
              <p className="result-excerpt">{h.excerpt}</p>
            </div>
          ))}
        </div>
      )}

      {results && hits.length === 0 && !loading && (
        <div className="empty-state">
          No results found. Try different keywords or use the Chat tab to ask Elbee directly.
        </div>
      )}
    </div>
  )
}
