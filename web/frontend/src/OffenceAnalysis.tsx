/**
 * Project Palantír — DEV-082-A3-2J-4C: aligned Offence and Magic presentation.
 * Author: Edward Turns (Project Lead)
 *
 * Display-only: never modifies metrics, scenario scoring or calibration.
 */
import './OffenceAnalysis.css'

type NeutralMelee = {
  unit: string
  benchmark: string
  conditions: string
  value_type: 'point' | 'interval'
  value: number | null
  lower: number
  upper: number
  qualifying_models: number
  unresolved_weapon_alternative_models: number
  is_overall_army_offence: false
  is_battlefield_forecast: false
}

type ConditionalCapabilities = {
  charge: {
    evidence: string
    known_qualified_profile_contribution_per_100pts: number
    full_profile_attribution: boolean
    empirical_charge_frequency: null
    additive_to_neutral_bar: false
  }
  support: {
    equipped_models: number
    legally_available_support_opportunities: null
    combat_bonus_value: null
    additive_to_neutral_bar: false
  }
  trapping: {
    frequency: null
    combat_bonus_value: null
    additive_to_neutral_bar: false
  }
  weapon_alternatives: {
    affected_models: number
    legal_selection_confirmed: false
    optimal_weapon_selected: false
  }
}

export type ProvisionalOffence = {
  stage: string
  status: 'provisional_display_only' | 'not_qualified'
  visibility: string
  reason_code?: string
  neutral_melee: NeutralMelee | null
  conditional_capabilities: ConditionalCapabilities | null
  safeguards: {
    production_scoring_changed: false
    calibration_changed: false
    candidate_raw_density: null
    promotion_authorised: false
  }
}

function readableReason(reason: string | undefined) {
  switch (reason) {
    case 'invalid_army': return 'The imported army could not be qualified.'
    case 'empty_army': return 'No fielded models were available for this reference.'
    case 'analysis_limit_exceeded': return 'This army exceeds the current analysis limits.'
    case 'unsupported_or_unverified_configuration':
      return 'Some profiles or equipment options are not yet verified for this benchmark.'
    default: return 'A qualified neutral melee reference is not available for this army.'
  }
}

const finite = (v: unknown): v is number =>
  typeof v === 'number' && Number.isFinite(v)

function isQualified(offence: ProvisionalOffence): boolean {
  const n = offence.neutral_melee
  const c = offence.conditional_capabilities
  const s = offence.safeguards
  return offence.status === 'provisional_display_only' &&
    offence.visibility === 'diagnostic_not_calibrated_not_overall_offence' &&
    n !== null && c !== null && s != null &&
    s.production_scoring_changed === false &&
    s.calibration_changed === false &&
    s.candidate_raw_density === null &&
    s.promotion_authorised === false &&
    n.benchmark === 'F4 S4 D6 A1 W1' &&
    n.conditions === 'one independent combat per model; uncharged; untrapped' &&
    n.is_overall_army_offence === false &&
    n.is_battlefield_forecast === false &&
    finite(n.lower) && finite(n.upper) && n.lower >= 0 && n.upper >= n.lower &&
    Number.isInteger(n.qualifying_models) && n.qualifying_models >= 0 &&
    Number.isInteger(n.unresolved_weapon_alternative_models) &&
    n.unresolved_weapon_alternative_models >= 0 &&
    (n.value_type === 'interval'
      ? n.value === null && n.unresolved_weapon_alternative_models > 0
      : n.value_type === 'point' && finite(n.value) &&
        Math.abs(n.value - n.lower) < 1e-8 &&
        Math.abs(n.upper - n.lower) < 1e-8 &&
        n.unresolved_weapon_alternative_models === 0) &&
    c.charge != null && c.support != null && c.trapping != null &&
    c.weapon_alternatives != null &&
    finite(c.charge.known_qualified_profile_contribution_per_100pts) &&
    c.charge.empirical_charge_frequency === null &&
    c.charge.additive_to_neutral_bar === false &&
    Number.isInteger(c.support.equipped_models) &&
    c.support.equipped_models >= 0 &&
    c.support.legally_available_support_opportunities === null &&
    c.support.combat_bonus_value === null &&
    c.support.additive_to_neutral_bar === false &&
    c.trapping.frequency === null &&
    c.trapping.combat_bonus_value === null &&
    c.trapping.additive_to_neutral_bar === false &&
    c.weapon_alternatives.affected_models === n.unresolved_weapon_alternative_models &&
    c.weapon_alternatives.legal_selection_confirmed === false &&
    c.weapon_alternatives.optimal_weapon_selected === false
}

/** Primary Offence text in the standard capability list, not a 0–1 rating. */
export function offenceHeadline(offence?: ProvisionalOffence | null): string {
  if (!offence || !isQualified(offence) || !offence.neutral_melee) return 'Not evaluated'
  const neutral = offence.neutral_melee
  return neutral.value_type === 'point'
    ? `${neutral.value!.toFixed(4)} (neutral melee)`
    : `${neutral.lower.toFixed(4)} – ${neutral.upper.toFixed(4)} (neutral melee)`
}

/**
 * Visual ruler only: the upper end is the highest *neutral-melee* value
 * observed in the six audited reference armies (Pits of Dol Guldur interval).
 * This is NOT the frozen 0–1 calibration or an overall Offence rating.
 */
const NEUTRAL_VISUAL_REFERENCE = 1.1000363336676016

export function OffenceHeadlineBar({ offence }: { offence?: ProvisionalOffence | null }) {
  if (!offence || !isQualified(offence) || !offence.neutral_melee) {
    return <div className="offence-track offence-track-unavailable" aria-label="Neutral melee benchmark unavailable" />
  }
  const neutral = offence.neutral_melee
  const minWidth = Math.max(0, Math.min(100, neutral.lower / NEUTRAL_VISUAL_REFERENCE * 100))
  const maxWidth = Math.max(minWidth, Math.min(100, neutral.upper / NEUTRAL_VISUAL_REFERENCE * 100))
  const interval = neutral.value_type === 'interval'
  const label = interval
    ? `Neutral melee density from ${neutral.lower.toFixed(4)} to ${neutral.upper.toFixed(4)} per 100 points`
    : `Neutral melee density ${neutral.lower.toFixed(4)} per 100 points`

  return (
    <div className="offence-bar-group">
      <div className="offence-track" role="img" aria-label={`${label}; visual reference range zero to ${NEUTRAL_VISUAL_REFERENCE.toFixed(4)}; not an overall Offence rating`}>
        <div className="offence-fill" style={{ width: `${maxWidth}%` }} />
        {interval && <div className="offence-interval" style={{ left: `${minWidth}%`, width: `${maxWidth - minWidth}%` }} />}
      </div>
      <div className="offence-reference-caption">
        Neutral melee reference · relative to six audited armies · not an overall rating
        {neutral.upper > NEUTRAL_VISUAL_REFERENCE && ' · exceeds visual reference'}
      </div>
    </div>
  )
}

/** Show expandable evidence within Offence's existing capability row. */
export function OffenceAnalysis({ offence }: { offence?: ProvisionalOffence | null }) {
  const qualified = offence !== null && offence !== undefined && isQualified(offence)
  const neutral = qualified ? offence!.neutral_melee! : null
  const caps = qualified ? offence!.conditional_capabilities! : null
  const unavailableText = offence?.status === 'not_qualified'
    ? readableReason(offence.reason_code)
    : 'No qualified mechanical melee evidence is available for this upload.'

  return (
    <details className="offence-details" data-testid="offence-details">
      <summary>View Offence analysis</summary>
      {neutral && caps ? (
        <div className="offence-content">
          <p className="offence-context">
            Neutral direct-melee density · {neutral.qualifying_models} qualified models
            {neutral.unresolved_weapon_alternative_models > 0 &&
              ` · ${neutral.unresolved_weapon_alternative_models} unresolved weapon alternatives`}
            {' · '}Benchmark {neutral.benchmark}; {neutral.conditions}.
          </p>
          <div className="offence-grid">
            <div className="offence-tile">
              <h3>Charging</h3>
              <p>Charge-parameter sensitivity: {caps.charge.known_qualified_profile_contribution_per_100pts.toFixed(4)} per 100 points.</p>
              <p>{caps.charge.full_profile_attribution
                ? 'Qualified profile attribution complete.'
                : 'Partial attribution; weapon alternatives remain.'}</p>
              <small>This is a legacy parameter comparison, not an observed charge frequency. A zero here does not imply the army cannot charge.</small>
            </div>
            <div className="offence-tile">
              <h3>Supporting attacks</h3>
              <p>{caps.support.equipped_models} {caps.support.equipped_models === 1
                ? 'model carries' : 'models carry'} potential support equipment.</p>
              <small>Actual support opportunities and their army-wide benefit depend on the battle.</small>
            </div>
            <div className="offence-tile">
              <h3>Trapping</h3>
              <p>Trapping changes combat outcomes when the required conditions are met.</p>
              <small>Battlefield trapping frequency is not assumed.</small>
            </div>
            <div className="offence-tile">
              <h3>Weapon alternatives</h3>
              <p>{caps.weapon_alternatives.affected_models} {caps.weapon_alternatives.affected_models === 1
                ? 'model has' : 'models have'} unresolved weapon alternatives.</p>
              <small>No weapon choice is automatically imposed. Intervals are retained when relevant.</small>
            </div>
          </div>
          <p className="capability-detail offence-disclosure">
            This measurement is not an overall Offence rating or a calibrated
            0–1 score. Charging, support and trapping are not added automatically.
          </p>
        </div>
      ) : (
        <div className="offence-unavailable" role="status">
          <strong>Neutral melee benchmark unavailable</strong>
          <p>{unavailableText}</p>
          <p>No value is shown; unavailable does not mean zero.</p>
        </div>
      )}
    </details>
  )
}
