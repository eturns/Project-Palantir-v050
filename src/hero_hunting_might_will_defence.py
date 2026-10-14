"""G3-B5B: exact declared Fate/Might decisions and verified Will protection.

Diagnostic-only; a separate state tracks Might because G3-B1 survival states
contain only Wounds/Fate/Will. Generic Will is NOT interchangeable with Fate.
"""
from dataclasses import dataclass
from fractions import Fraction
from collections import defaultdict

@dataclass(frozen=True, order=True)
class DefenceResources:
    wounds: int
    fate: int
    will: int
    might: int
    def __post_init__(self):
        for key in ("wounds","fate","will","might"):
            v=getattr(self,key)
            if isinstance(v,bool) or not isinstance(v,int) or v<0:
                raise ValueError(f"{key} must be a non-negative integer")

@dataclass(frozen=True)
class VerifiedWillProtection:
    source: str
    save_probability: Fraction
    def __post_init__(self):
        if not isinstance(self.source,str) or not self.source.strip():
            raise ValueError("verified Will rule source required")
        if not isinstance(self.save_probability,Fraction) or not 0<=self.save_probability<=1:
            raise ValueError("verified Will save probability required")

@dataclass(frozen=True)
class DefencePolicy:
    fate_attempt_limit: int = 0
    might_limit_per_fate_roll: int = 0
    use_will_if_no_fate_save: bool = False
    verified_will_protection: VerifiedWillProtection | None = None
    def __post_init__(self):
        for key in ("fate_attempt_limit","might_limit_per_fate_roll"):
            v=getattr(self,key)
            if isinstance(v,bool) or not isinstance(v,int) or v<0:
                raise ValueError(f"{key} must be a non-negative integer")
        if not isinstance(self.use_will_if_no_fate_save,bool):
            raise TypeError("use_will_if_no_fate_save must be bool")
        if self.use_will_if_no_fate_save and not isinstance(
            self.verified_will_protection,VerifiedWillProtection
        ):
            raise ValueError("Will-as-protection requires verified special rule")
        if not self.use_will_if_no_fate_save and self.verified_will_protection is not None:
            raise ValueError("unrequested Will protection is unsupported")

def defended_wound_distribution(
    state: DefenceResources,
    incoming_wound_probability: Fraction,
    policy: DefencePolicy,
) -> dict[DefenceResources,Fraction]:
    """Exact D6 branching. Might improves 1-3 only if enough Might and cap.

    Per declared policy: use minimum Might needed to turn 1-3 into 4,
    otherwise proceed to next Fate point. Will is attempted only after
    Fate attempts fail or are unavailable, with independently verified
    per-point prevention probability. Rule ordering is explicitly a caller
    policy, not inferred from generic MESBG rules.
    """
    if not isinstance(state,DefenceResources) or state.wounds==0:
        raise ValueError("living DefenceResources required")
    if not isinstance(policy,DefencePolicy):
        raise TypeError("DefencePolicy required")
    p=incoming_wound_probability
    if not isinstance(p,Fraction) or not 0<=p<=1:
        raise ValueError("incoming_wound_probability must be Fraction within [0,1]")
    out=defaultdict(Fraction)
    out[state]+=1-p

    def finish(s, mass):
        if policy.use_will_if_no_fate_save and s.will>0:
            q=policy.verified_will_protection.save_probability
            out[DefenceResources(s.wounds,s.fate,s.will-1,s.might)] += mass*q
            out[DefenceResources(s.wounds-1,s.fate,s.will-1,s.might)] += mass*(1-q)
        else:
            out[DefenceResources(s.wounds-1,s.fate,s.will,s.might)] += mass

    def try_fate(s, mass, rolled):
        if mass==0:
            return
        if rolled>=min(policy.fate_attempt_limit,state.fate) or s.fate==0:
            finish(s,mass)
            return
        for die in range(1,7):
            branch=mass/6
            after=DefenceResources(s.wounds,s.fate-1,s.will,s.might)
            if die>=4:
                out[after]+=branch
            else:
                cost=4-die
                if cost<=s.might and cost<=policy.might_limit_per_fate_roll:
                    out[DefenceResources(after.wounds,after.fate,after.will,after.might-cost)] += branch
                else:
                    try_fate(after,branch,rolled+1)

    try_fate(state,p,0)
    return {s:prob for s,prob in out.items() if prob}

def evaluate_defended_sequence(
    state: DefenceResources,
    events: tuple[tuple[str,Fraction,DefencePolicy],...],
) -> dict[DefenceResources,Fraction]:
    """Ordered explicit probabilities only; no assumed independent per-event roll."""
    if not isinstance(events,tuple):
        raise TypeError("events must be tuple")
    distribution={state:Fraction(1)}
    seen=set()
    for event in events:
        if not isinstance(event,tuple) or len(event)!=3:
            raise TypeError("each event must be (id, probability, policy)")
        key,p,policy=event
        if not isinstance(key,str) or not key.strip() or key in seen:
            raise ValueError("event identifiers must be nonblank and unique")
        seen.add(key)
        next_dist=defaultdict(Fraction)
        for s,mass in distribution.items():
            if s.wounds==0:
                next_dist[s]+=mass
            else:
                for after,prob in defended_wound_distribution(s,p,policy).items():
                    next_dist[after]+=mass*prob
        distribution=dict(next_dist)
    return distribution
