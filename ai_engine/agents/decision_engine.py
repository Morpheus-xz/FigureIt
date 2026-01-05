from typing import Dict
import os
from openai import OpenAI

from ai_engine.models.user_state import UserState, DecisionState
from ai_engine.market.market_pulse import MarketPulse


# =====================================================
# CAREER SPACE
# =====================================================

CAREER_PATHS = [
    "Frontend Engineering",
    "Backend Engineering",
    "Data Science / ML",
    "Competitive Programming"
]

PATH_DIFFICULTY = {
    "Frontend Engineering": 0.2,
    "Backend Engineering": 0.3,
    "Data Science / ML": 0.6,
    "Competitive Programming": 0.4
}

PATH_TO_MARKET_SKILLS = {
    "Frontend Engineering": ["React", "Next.js"],
    "Backend Engineering": ["Python", "Java", "Node.js"],
    "Data Science / ML": ["Python", "TensorFlow"],
    "Competitive Programming": ["Algorithms"]
}


# =====================================================
# FEATURE EXTRACTION
# =====================================================

def extract_features(user: UserState) -> Dict[str, float]:
    ev = user.evidence_profile
    gh = ev.github_stats
    lc = ev.leetcode_stats
    bias = user.interest_profile.interest_bias

    return {
        "project_strength": min(gh.get("stars", 0) / 10, 1.0),
        "project_volume": min(gh.get("repos", 0) / 10, 1.0),
        "dsa_depth": min(lc.get("medium", 0) / 40, 1.0),
        "easy_bias": min(
            lc.get("easy", 0) / max(lc.get("total_solved", 1), 1),
            1.0
        ),
        "interest_dev": bias.get("development", 0.0),
        "interest_ps": bias.get("problem_solving", 0.0),
        "interest_data": bias.get("data", 0.0),
    }


# =====================================================
# BASE SCORE (NO MARKET)
# =====================================================

def score_path(path: str, f: Dict[str, float], hours: int) -> float:
    score = 0.0

    if path == "Frontend Engineering":
        score = 0.4*f["project_strength"] + 0.2*f["project_volume"] + 0.4*f["interest_dev"]

    elif path == "Backend Engineering":
        score = 0.3*f["project_strength"] + 0.2*f["dsa_depth"] + 0.3*f["interest_dev"] + 0.2*f["interest_ps"]

    elif path == "Data Science / ML":
        score = 0.4*f["dsa_depth"] + 0.4*f["interest_data"] - 0.2*f["easy_bias"]

    elif path == "Competitive Programming":
        score = 0.5*f["dsa_depth"] + 0.3*f["interest_ps"] - 0.2*f["easy_bias"]

    difficulty = PATH_DIFFICULTY[path]
    if hours < 10:
        score -= difficulty * 0.6
    elif hours < 15:
        score -= difficulty * 0.3

    return max(score, 0.0)


# =====================================================
# FINAL DECISION ENGINE (FIXED)
# =====================================================

def make_decision(user: UserState) -> UserState:
    """
    Market-aware decision engine.
    MarketPulse is owned internally.
    """

    features = extract_features(user)
    hours = user.basic_profile.time_availability
    max_focus = user.context_profile.max_focus_skills

    market = MarketPulse(
        client=OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    )

    scores = {}
    reasons = {}

    for path in CAREER_PATHS:
        base = score_path(path, features, hours)

        skills = PATH_TO_MARKET_SKILLS.get(path, [])
        market_multiplier = (
            sum(market.get_market_multiplier(s) for s in skills) / len(skills)
            if skills else 1.0
        )

        final = round(base * market_multiplier, 3)
        scores[path] = final
        reasons[path] = f"Score {final} (market {round(market_multiplier,2)}x)"

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    focus, park, drop = [], [], []

    for path, score in ranked:
        if score < 0.25:
            drop.append(path)
        elif len(focus) < max_focus:
            focus.append(path)
        else:
            park.append(path)

    if not focus:
        focus.append(ranked[0][0])

    user.decision_state = DecisionState(
        focus=focus,
        park=park,
        drop=drop,
        reasons=reasons
    )

    return user
