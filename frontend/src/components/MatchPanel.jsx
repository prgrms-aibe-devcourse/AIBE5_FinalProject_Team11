import { useState } from 'react'

const GOALS = [
  { id: 'Spinal_Mobility',   label: 'Spinal Mobility',   emoji: '🔄' },
  { id: 'Back_Pain_Relief',  label: 'Back Pain Relief',  emoji: '🩹' },
  { id: 'Core_Strength',     label: 'Core Strength',     emoji: '💪' },
  { id: 'Hip_Flexibility',   label: 'Hip Flexibility',   emoji: '🦯' },
  { id: 'Balance',           label: 'Balance',           emoji: '⚖️' },
  { id: 'Stress_Relief',     label: 'Stress Relief',     emoji: '🌿' },
  { id: 'Shoulder_Opening',  label: 'Shoulder Opening',  emoji: '🙆' },
  { id: 'Strength',          label: 'Overall Strength',  emoji: '🏋️' },
]

const HEALTH_FLAGS_OPTIONS = [
  'herniated disc',
  'knee injury',
  'wrist injury',
  'high blood pressure',
  'pregnancy',
  'shoulder injury',
]

export default function MatchPanel() {
  const [selectedGoals,  setSelectedGoals]  = useState([])
  const [healthFlags,    setHealthFlags]    = useState([])
  const [topK,           setTopK]           = useState(5)
  const [userId,         setUserId]         = useState('')
  const [results,        setResults]        = useState(null)
  const [loading,        setLoading]        = useState(false)
  const [error,          setError]          = useState('')
  const [step,           setStep]           = useState(1) // onboarding wizard steps

  function toggleGoal(id) {
    setSelectedGoals(prev =>
      prev.includes(id) ? prev.filter(g => g !== id) : [...prev, id]
    )
  }

  function toggleFlag(flag) {
    setHealthFlags(prev =>
      prev.includes(flag) ? prev.filter(f => f !== flag) : [...prev, flag]
    )
  }

  async function submitMatch() {
    if (selectedGoals.length === 0) {
      setError('Please select at least one goal.')
      return
    }

    setLoading(true)
    setError('')
    setResults(null)

    const body = {
      goals: selectedGoals,
      topK,
      ...(healthFlags.length > 0 && { healthFlags }),
      ...(userId.trim() && { userId: userId.trim() }),
    }

    try {
      const res = await fetch('/api/v1/match', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })
      if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText}`)
      const data = await res.json()
      setResults(data)
      setStep(3)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  function reset() {
    setSelectedGoals([])
    setHealthFlags([])
    setTopK(5)
    setUserId('')
    setResults(null)
    setError('')
    setStep(1)
  }

  const poses = results?.poses ?? results?.matches ?? []

  return (
    <div className="match-panel">
      {/* Onboarding steps indicator */}
      <div className="wizard-steps">
        {['1. Your Goals', '2. Health Info', '3. Results'].map((label, i) => (
          <div
            key={i}
            className={`wizard-step ${step === i + 1 ? 'active' : ''} ${step > i + 1 ? 'done' : ''}`}
          >
            <span className="step-num">{step > i + 1 ? '✓' : i + 1}</span>
            <span className="step-label">{label}</span>
          </div>
        ))}
      </div>

      {/* Step 1: Goal selection */}
      {step === 1 && (
        <div className="wizard-content">
          <h2>What are your yoga goals?</h2>
          <p className="wizard-hint">Select one or more goals. The matching system will find poses from 809 poses scored against your selections.</p>

          <div className="goals-grid">
            {GOALS.map(goal => (
              <button
                key={goal.id}
                className={`goal-card ${selectedGoals.includes(goal.id) ? 'selected' : ''}`}
                onClick={() => toggleGoal(goal.id)}
              >
                <span className="goal-emoji">{goal.emoji}</span>
                <span className="goal-label">{goal.label}</span>
                {selectedGoals.includes(goal.id) && <span className="goal-check">✓</span>}
              </button>
            ))}
          </div>

          <div className="wizard-nav">
            <button
              className="btn-primary"
              disabled={selectedGoals.length === 0}
              onClick={() => setStep(2)}
            >
              Continue →
            </button>
          </div>
        </div>
      )}

      {/* Step 2: Health flags + settings */}
      {step === 2 && (
        <div className="wizard-content">
          <h2>Any health considerations?</h2>
          <p className="wizard-hint">Optional. Select any conditions so poses with contraindications are filtered out safely.</p>

          <div className="flags-grid">
            {HEALTH_FLAGS_OPTIONS.map(flag => (
              <button
                key={flag}
                className={`flag-card ${healthFlags.includes(flag) ? 'selected' : ''}`}
                onClick={() => toggleFlag(flag)}
              >
                {healthFlags.includes(flag) ? '⚠️' : '○'} {flag}
              </button>
            ))}
          </div>

          <div className="topk-row">
            <label htmlFor="topk-slider">
              Number of poses to recommend: <strong>{topK}</strong>
            </label>
            <input
              id="topk-slider"
              type="range"
              min={1}
              max={20}
              value={topK}
              onChange={e => setTopK(Number(e.target.value))}
              className="topk-slider"
            />
          </div>

          <div className="userid-row">
            <label htmlFor="user-id">User ID (optional)</label>
            <input
              id="user-id"
              type="text"
              value={userId}
              onChange={e => setUserId(e.target.value)}
              placeholder="e.g. user_123"
              className="text-input"
            />
          </div>

          {error && <div className="error-banner">⚠️ {error}</div>}

          <div className="wizard-nav">
            <button className="btn-secondary" onClick={() => setStep(1)}>← Back</button>
            <button
              className="btn-primary"
              onClick={submitMatch}
              disabled={loading}
            >
              {loading ? '⏳ Matching…' : '✨ Find My Poses'}
            </button>
          </div>
        </div>
      )}

      {/* Step 3: Results */}
      {step === 3 && (
        <div className="wizard-content">
          <div className="results-header">
            <div>
              <h2>Your Recommended Poses</h2>
              <p className="wizard-hint">
                Based on: {selectedGoals.map(g => g.replace(/_/g, ' ')).join(', ')}
              </p>
            </div>
            <button className="btn-secondary" onClick={reset}>Start Over</button>
          </div>

          {error && <div className="error-banner">⚠️ {error}</div>}

          {poses.length === 0 && !error && (
            <div className="empty-state">
              <p>No poses returned. The matching API returned an empty result.</p>
              <p style={{ fontSize: '0.85rem', color: '#888', marginTop: '0.5rem' }}>
                Note: The scoring engine is currently being calibrated (T-001). Results will improve once goal↔tag alignment is fixed.
              </p>
            </div>
          )}

          <div className="pose-results">
            {poses.map((pose, i) => (
              <div key={i} className="pose-card">
                <div className="pose-rank">#{i + 1}</div>
                <div className="pose-info">
                  <div className="pose-name">
                    {pose.commonName ?? pose.common_name ?? pose.name ?? pose.poseId ?? pose.pose_id ?? `Pose ${i + 1}`}
                  </div>
                  {(pose.canonicalName ?? pose.canonical_name) && (
                    <div className="pose-sanskrit">
                      {pose.canonicalName ?? pose.canonical_name}
                    </div>
                  )}
                  <div className="pose-meta">
                    {pose.difficulty !== undefined && (
                      <span className="pose-badge">
                        {'⭐'.repeat(Math.min(pose.difficulty, 5))} Difficulty {pose.difficulty}
                      </span>
                    )}
                    {(pose.score !== undefined && pose.score !== null) && (
                      <span className="pose-badge score-badge">
                        Score: {typeof pose.score === 'number' ? pose.score.toFixed(2) : pose.score}
                      </span>
                    )}
                  </div>
                  {pose.naturalDescription ?? pose.natural_description ? (
                    <p className="pose-desc">
                      {(pose.naturalDescription ?? pose.natural_description).slice(0, 160)}…
                    </p>
                  ) : null}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
