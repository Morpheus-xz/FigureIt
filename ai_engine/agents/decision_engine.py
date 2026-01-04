"""
Decision Engine — FigureIt (v5.0 FINAL)

ROLE:
- Convert numeric signals into FOCUS / PARK / DROP decisions
- Fully data-driven (NO string rules, NO hard-coded flags)
- ML-replaceable without refactor

CORE IDEA:
Each career path receives a viability score based on:
- Evidence strength
- Interest alignment
- Context constraints (time & focus limits)
"""

from typing import Dict
from ai_engine.models.user_state import UserState, DecisionState


# =====================================================
# CAREER SPACE
# =====================================================

CAREER_PATHS = [
    "Frontend Engineering",
    "Backend Engineering",
    "Data Science / ML",
    "Competitive Programming"
]

# Difficulty multipliers (used ONLY as context penalty)
PATH_DIFFICULTY = {
    "Frontend Engineering": 0.2,
    "Backend Engineering": 0.3,
    "Data Science / ML": 0.6,
    "Competitive Programming": 0.4
}


# =====================================================
# FEATURE EXTRACTION (PURE NUMERIC)
# =====================================================

def extract_features(user: UserState) -> Dict[str, float]:
    """
    Converts Evidence + Interests into a numeric feature vector (0–1).
    """
    ev = user.evidence_profile
    gh = ev.github_stats
    lc = ev.leetcode_stats
    bias = user.interest_profile.interest_bias

    features = {
        # ---------- Project Signals ----------
        "project_strength": min(gh.get("stars", 0) / 10, 1.0),
        "project_volume": min(gh.get("repos", 0) / 10, 1.0),

        # ---------- DSA Signals ----------
        "dsa_depth": min(lc.get("medium", 0) / 40, 1.0),
        "dsa_volume": min(lc.get("total_solved", 0) / 300, 1.0),
        "easy_bias": min(
            (lc.get("easy", 0) / max(lc.get("total_solved", 1), 1)),
            1.0
        ),

        # ---------- Interest Signals ----------
        "interest_dev": bias.get("development", 0.0),
        "interest_ps": bias.get("problem_solving", 0.0),
        "interest_data": bias.get("data", 0.0),
    }

    return features


# =====================================================
# SCORING LOGIC
# =====================================================

def score_path(
    path: str,
    f: Dict[str, float],
    hours: int
) -> float:
    """
    Computes final viability score for a career path.
    """

    score = 0.0

    if path == "Frontend Engineering":
        score += (
            0.4 * f["project_strength"] +
            0.2 * f["project_volume"] +
            0.4 * f["interest_dev"]
        )

    elif path == "Backend Engineering":
        score += (
            0.3 * f["project_strength"] +
            0.2 * f["dsa_depth"] +
            0.3 * f["interest_dev"] +
            0.2 * f["interest_ps"]
        )

    elif path == "Data Science / ML":
        score += (
            0.4 * f["dsa_depth"] +
            0.4 * f["interest_data"] -
            0.2 * f["easy_bias"]
        )

    elif path == "Competitive Programming":
        score += (
            0.5 * f["dsa_depth"] +
            0.3 * f["interest_ps"] -
            0.2 * f["easy_bias"]
        )

    # ---------- Context Penalty ----------
    difficulty = PATH_DIFFICULTY[path]
    if hours < 10:
        score -= difficulty * 0.6
    elif hours < 15:
        score -= difficulty * 0.3

    return round(max(score, 0.0), 3)


# =====================================================
# MAIN ENTRY
# =====================================================

def make_decision(user: UserState) -> UserState:
    """
    Produces FOCUS / PARK / DROP decisions.
    """

    features = extract_features(user)
    hours = user.basic_profile.time_availability
    max_focus = user.context_profile.max_focus_skills

    scores = {
        path: score_path(path, features, hours)
        for path in CAREER_PATHS
    }

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    focus, park, drop, reasons = [], [], [], {}

    for path, score in ranked:
        if score < 0.25:
            drop.append(path)
            reasons[path] = f"Low viability score ({score})."
        elif len(focus) < max_focus:
            focus.append(path)
            reasons[path] = f"Best alignment score ({score})."
        else:
            park.append(path)
            reasons[path] = f"Good option ({score}) but focus limit reached."

    if not focus:
        focus.append(ranked[0][0])
        reasons[ranked[0][0]] = "Fallback choice due to weak overall signals."

    user.decision_state = DecisionState(
        focus=focus,
        park=park,
        drop=drop,
        reasons=reasons
    )

    return user
