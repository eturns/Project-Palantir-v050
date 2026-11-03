import { useState, type ChangeEvent } from 'react'
import './App.css'

type Capability = {
  metric_id: string
  label: string
  rating: number | null
  raw_value: number | null
  status: string
  unit: string | null
  explanation: string
  clipped: boolean
}

type Assessment = {
  metric: string
  rating: string
  value: number
}

type Scenario = {
  scenario_id: string
  name: string
  pool: string
  score: number
}

type ArmyAnalysis = {
  army_name: string
  total_points: number
  points_limit: number | null
  model_count: number | null
  might: number | null
  will: number | null
  fate: number | null
  provisional_capabilities: {
    title: string
    display_only: boolean
    metrics: Capability[]
  }
  strengths: Assessment[]
  weaknesses: Assessment[]
  scenarios: Scenario[]
}

type AnalysisResponse = {
  schema_version: string
  analysis: ArmyAnalysis
}

function App() {
  const [army, setArmy] = useState<ArmyAnalysis | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleFile(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0]
    if (!file) return

    setLoading(true)
    setError('')
    setArmy(null)

    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await fetch('/api/v1/analyse', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error(`Army analysis failed (HTTP ${response.status})`)
      }

      const result: AnalysisResponse = await response.json()

      if (result.schema_version !== 'palantir-web-analysis-v1') {
        throw new Error('Unsupported analysis response version')
      }

      if (
        !Array.isArray(result.analysis?.provisional_capabilities?.metrics) ||
        result.analysis.provisional_capabilities.display_only !== true ||
        !Array.isArray(result.analysis.scenarios) ||
        !result.analysis.scenarios.every(
          scenario =>
            typeof scenario.scenario_id === 'string' &&
            typeof scenario.name === 'string' &&
            typeof scenario.score === 'number' &&
            Number.isFinite(scenario.score)
        )
      ) {
        throw new Error('Invalid analysis response')
      }

      setArmy(result.analysis)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed')
    } finally {
      setLoading(false)
      event.target.value = ''
    }
  }

  // Rankings are presentation only.
  // No scenario calculations or adjustments are performed.
  const rankedScenarios = army
    ? [...army.scenarios].sort(
        (a, b) =>
          b.score - a.score ||
          a.scenario_id.localeCompare(b.scenario_id)
      )
    : []

  const topScenarios = rankedScenarios.slice(0, 5)

  const bottomScenarios = [...rankedScenarios]
    .reverse()
    .slice(0, 5)

  return (
    <main className="palantir">
      <header className="header">
        <div className="brand">PROJECT PALANTÍR</div>
        <p>Middle-earth Strategy Battle Game • Army Analysis</p>
      </header>

      <section className="panel">
        <h1>Understand your army.</h1>
        <p>
          Upload an MESBG List Builder JSON export to analyse
          your army using the Project Palantír engine.
        </p>

        <label className="upload-button">
          {loading ? 'Analysing army...' : 'Upload Army JSON'}
          <input
            type="file"
            accept=".json,application/json"
            onChange={handleFile}
            disabled={loading}
            hidden
          />
        </label>

        {error && <p className="error" role="alert">{error}</p>}
      </section>

      {army && (
        <>
          <section className="panel">
            <h2>{army.army_name}</h2>
            <p className="subtitle">Analysis complete</p>

            <div className="stats">
              {[
                ['Army Points', `${army.total_points} / ${army.points_limit ?? '—'}`],
                ['Models', army.model_count ?? '—'],
                ['Might', army.might ?? '—'],
                ['Will', army.will ?? '—'],
                ['Fate', army.fate ?? '—'],
              ].map(([label, value]) => (
                <div className="stat" key={label}>
                  <span>{label}</span>
                  <strong>{value}</strong>
                </div>
              ))}
            </div>
          </section>

          <section className="panel">
            <h2>Army Capability Analysis</h2>
            <p className="subtitle">
              Provisional six-army calibration • Display only
            </p>

            <div className="capability-list">
              {army.provisional_capabilities.metrics.map((capability) => {
                const evaluated =
                  capability.status === 'evaluated' &&
                  capability.rating !== null &&
                  Number.isFinite(capability.rating)

                const score = evaluated
                  ? Math.max(0, Math.min(1, capability.rating!))
                  : null

                return (
                  <div className="capability" key={capability.metric_id}>
                    <div className="capability-heading">
                      <strong>{capability.label}</strong>
                      <span>
                        {score !== null
                          ? score.toFixed(3)
                          : capability.status === 'conditional'
                            ? 'Conditional — Not evaluated'
                            : 'Not evaluated'}
                      </span>
                    </div>

                    <div
                      className="capability-track"
                      role={score === null ? undefined : 'progressbar'}
                      aria-label={capability.label}
                      aria-valuemin={score === null ? undefined : 0}
                      aria-valuemax={score === null ? undefined : 1}
                      aria-valuenow={score ?? undefined}
                    >
                      {score !== null && (
                        <div
                          className="capability-fill"
                          style={{ width: `${score * 100}%` }}
                        />
                      )}
                    </div>

                    <div className="capability-detail">
                      {evaluated && capability.raw_value !== null
                        ? `Raw: ${capability.raw_value.toFixed(3)} ${capability.unit ?? ''}`
                        : 'No qualified numerical measurement'}

                      {capability.clipped && ' • Clipped to reference range'}
                    </div>
                  </div>
                )
              })}
            </div>

            <p className="capability-note">
              These provisional ratings compare armies against the
              frozen six-army reference, not against the full range
              of possible MESBG armies. Unavailable measurements are
              never treated as zero. Scenario scores are unchanged.
            </p>
          </section>

          <section className="panel">
            <h2>Strengths &amp; Weaknesses</h2>
            <p className="subtitle">
              Existing battlefield assessments ? Legacy scoring
            </p>

            <div className="scenario-grid">
              <div className="scenario-group">
                <h3 className="scenario-best">Army Strengths</h3>
                {army.strengths.length === 0 ? (
                  <p>No strengths identified.</p>
                ) : (
                  army.strengths.map((item) => (
                    <div className="scenario-row" key={item.metric}>
                      <div className="scenario-info">
                        <strong>{item.metric}</strong>
                        <small>{item.rating}</small>
                      </div>
                      <div className="scenario-score best-score">
                        {item.value.toFixed(3)}
                      </div>
                    </div>
                  ))
                )}
              </div>

              <div className="scenario-group">
                <h3 className="scenario-worst">Army Weaknesses</h3>
                {army.weaknesses.length === 0 ? (
                  <p>No weaknesses identified.</p>
                ) : (
                  army.weaknesses.map((item) => (
                    <div className="scenario-row" key={item.metric}>
                      <div className="scenario-info">
                        <strong>{item.metric}</strong>
                        <small>{item.rating}</small>
                      </div>
                      <div className="scenario-score worst-score">
                        {item.value.toFixed(3)}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>

            <p className="capability-note">
              These assessments use existing battlefield ratings.
              They are separate from the provisional mechanical
              capability measurements shown above.
            </p>
          </section>

          <section className="panel">
            <h2>Scenario Analysis</h2>
            <p className="subtitle">
              {rankedScenarios.length} scenarios analysed
              {' • '}Existing engine scores
            </p>

            {rankedScenarios.length === 0 ? (
              <p>No scenario results are available for this army.</p>
            ) : (
              <div className="scenario-grid">
                <div className="scenario-group">
                  <h3 className="scenario-best">Top 5 Scenarios</h3>

                  {topScenarios.map((scenario, index) => (
                    <div
                      className="scenario-row"
                      key={scenario.scenario_id}
                    >
                      <div className="scenario-position">
                        {index + 1}
                      </div>
                      <div className="scenario-info">
                        <strong>{scenario.name}</strong>
                        <small>{scenario.pool.replaceAll('_', ' ')}</small>
                      </div>
                      <div className="scenario-score best-score">
                        {scenario.score.toFixed(3)}
                      </div>
                    </div>
                  ))}
                </div>

                <div className="scenario-group">
                  <h3 className="scenario-worst">Bottom 5 Scenarios</h3>

                  {bottomScenarios.map((scenario, index) => (
                    <div
                      className="scenario-row"
                      key={scenario.scenario_id}
                    >
                      <div className="scenario-position">
                        {index + 1}
                      </div>
                      <div className="scenario-info">
                        <strong>{scenario.name}</strong>
                        <small>{scenario.pool.replaceAll('_', ' ')}</small>
                      </div>
                      <div className="scenario-score worst-score">
                        {scenario.score.toFixed(3)}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <p className="capability-note">
              Scenario rankings use existing Palantír scores.
              They have not been recalculated using the
              provisional capability measurements.
            </p>
          </section>
        </>
      )}

      <footer>
        Project Palantír • DEV-079 Web Prototype
      </footer>
    </main>
  )
}

export default App