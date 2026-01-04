"""
Context Profiler Agent — FigureIt (v1.1)

ROLE:
- Determines the "Difficulty Mode" of the user's career path.
- Sets strict limits on how many things a user can learn at once.
- Decides if "Code" is enough or if "Deployment" is needed (ProofExpectation).

LOGIC PHILOSOPHY:
- Tier 3 students need STRONGER proof to get the same results.
- Final year students (High Urgency) cannot afford split focus.
- Low time availability (< 10h) forces single-tasking.
"""

from ai_engine.models.user_state import (
    UserState,
    ContextProfile,
    Strictness,
    Urgency,
    ProofExpectation,
    Confidence
)


def build_context(user_state: UserState) -> UserState:
    """
    Builds and attaches ContextProfile to UserState.
    Idempotent: runs only once.
    """

    # 1. IDEMPOTENCY GUARD
    if user_state.context_profile is not None:
        return user_state

    basic = user_state.basic_profile
    interest = user_state.interest_profile

    # -------------------------
    # 1. URGENCY LOGIC (Time left to get hired)
    # -------------------------
    if basic.year_of_study >= 4:
        urgency = Urgency.HIGH
    elif basic.year_of_study == 3:
        urgency = Urgency.MEDIUM
    else:
        # 1st & 2nd years have time to explore
        urgency = Urgency.LOW

    # -------------------------
    # 2. STRICTNESS LOGIC (The "Filter" Strength)
    # -------------------------
    # Default baseline
    strictness = Strictness.MEDIUM

    # A. The "Tier Tax": Tier 3 needs strict portfolios earlier
    if basic.college_tier == 3 and basic.year_of_study >= 3:
        strictness = Strictness.HIGH

    # B. The "Bandwidth" Constraint: Low time = High strictness
    if basic.time_availability < 8:
        strictness = Strictness.HIGH

    # C. The "Safety Net": Tier 1 juniors get leeway
    if basic.college_tier == 1 and basic.year_of_study <= 2:
        strictness = Strictness.LOW

    # -------------------------
    # 3. MAX FOCUS SKILLS (Elimination Logic)
    # -------------------------
    # Rule: If Urgency is HIGH (Final Year), you assume you need a job NOW.
    # You cannot split focus.
    if urgency == Urgency.HIGH:
        max_focus = 1
    elif strictness == Strictness.HIGH:
        max_focus = 1
    else:
        # We never allow 3. That causes tutorial hell. Cap at 2.
        max_focus = 2

    # -------------------------
    # 4. PROOF EXPECTATION (What counts as "Done"?)
    # -------------------------
    # Tier 3 OR High Urgency requires "Strong" proof (Deployed/Live)
    # Tier 1 or Juniors can get away with "Basic" proof (GitHub Code)
    if basic.college_tier == 3 or urgency == Urgency.HIGH:
        proof = ProofExpectation.STRONG
    else:
        proof = ProofExpectation.BASIC

    # -------------------------
    # 5. ATTACH TO STATE
    # -------------------------
    user_state.context_profile = ContextProfile(
        strictness_level=strictness,
        urgency_level=urgency,
        max_focus_skills=max_focus,
        proof_expectation=proof
    )

    return user_state