"""
Evidence Profiler Agent — FigureIt (v2 - God Level)

ROLE:
- Interprets raw data into 'Behavioral Flags'.
- Detects specific user Archetypes (The Theorist, The Builder, The Ghost).
- Uses tunable thresholds for stricter/looser judgment.

INPUT: Raw GitHub & LeetCode stats
OUTPUT: EvidenceProfile attached to UserState
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from ai_engine.models.user_state import UserState, EvidenceProfile

# =====================================================
# TUNABLE THRESHOLDS (The "Bar")
# =====================================================
THRESHOLDS = {
    # GitHub
    "MIN_REPOS": 3,
    "TUTORIAL_HELL_REPOS": 10,
    "IMPACT_STARS": 5,  # At least 5 strangers liked your code
    "SENIOR_ACCOUNT_YEARS": 3,

    # LeetCode
    "DSA_GHOST_LIMIT": 15,
    "EASY_FARMER_RATIO": 0.7,  # >70% Easy = Red Flag
    "INTERVIEW_READY_MEDIUMS": 30,
    "COMPETITIVE_HARDS": 10
}


def _calculate_account_age(created_at: str) -> float:
    """Returns account age in years."""
    if not created_at: return 0.0
    try:
        start = datetime.strptime(created_at, "%Y-%m-%d")
        now = datetime.now()
        return (now - start).days / 365.0
    except:
        return 0.0


def build_evidence(
        user_state: UserState,
        github_stats: Optional[Dict[str, Any]],
        leetcode_stats: Optional[Dict[str, Any]]
) -> UserState:
    """
    Builds EvidenceProfile with Archetype Detection.
    """
    flags: List[str] = []

    # -------------------------
    # 1. GITHUB DEEP DIVE
    # -------------------------
    gh_valid = github_stats and github_stats.get("valid")

    if not gh_valid:
        flags.append("no_github_evidence")
        # Set defaults to safe 0 to prevent logic errors below
        repo_count = 0
        stars = 0
        age = 0.0
    else:
        repo_count = github_stats.get("repos", 0)
        stars = github_stats.get("stars", 0)
        age = _calculate_account_age(github_stats.get("account_created", ""))

        # --- Activity Flags ---
        if repo_count == 0:
            flags.append("github_ghost")
        elif repo_count < THRESHOLDS["MIN_REPOS"]:
            flags.append("low_output")  # Has account, but barely uses it

        # --- Quality Flags ---
        # "Tutorial Hell": High quantity, Zero impact
        if repo_count > THRESHOLDS["TUTORIAL_HELL_REPOS"] and stars == 0:
            flags.append("tutorial_hell_confirmed")

        # "Impact": People actually use their code
        if stars >= THRESHOLDS["IMPACT_STARS"]:
            flags.append("proven_impact")

        # "Stagnant": Old account, low repos (The "I made this in 1st year" student)
        if age > THRESHOLDS["SENIOR_ACCOUNT_YEARS"] and repo_count < 5:
            flags.append("stagnant_developer")

    # -------------------------
    # 2. LEETCODE DEEP DIVE
    # -------------------------
    lc_valid = leetcode_stats and leetcode_stats.get("valid")

    if not lc_valid:
        flags.append("no_dsa_evidence")
        total = 0
        easy, medium, hard = 0, 0, 0
    else:
        total = leetcode_stats.get("total_solved", 0)
        easy = leetcode_stats.get("easy", 0)
        medium = leetcode_stats.get("medium", 0)
        hard = leetcode_stats.get("hard", 0)

        # --- Effort Flags ---
        if total < THRESHOLDS["DSA_GHOST_LIMIT"]:
            flags.append("dsa_beginner")

        # --- Quality Flags ---
        # "Easy Farmer": Solves 100 problems, 90 are Easy.
        if total > 50:
            easy_ratio = easy / total
            if easy_ratio > THRESHOLDS["EASY_FARMER_RATIO"]:
                flags.append("easy_farmer")

        # "Interview Ready": Can handle Mediums (The sweet spot)
        if medium >= THRESHOLDS["INTERVIEW_READY_MEDIUMS"]:
            flags.append("interview_ready_dsa")

        # "Competitive": Solves Hards
        if hard >= THRESHOLDS["COMPETITIVE_HARDS"]:
            flags.append("competitive_programmer")

    # -------------------------
    # 3. ARCHETYPE DETECTION (The God Level)
    # -------------------------
    # Cross-referencing both platforms to find the "Persona"

    # "The Builder": Good GitHub, No DSA
    if "proven_impact" in flags and ("dsa_beginner" in flags or "no_dsa_evidence" in flags):
        flags.append("archetype_builder")

    # "The Theorist": Good DSA, No Projects
    elif "interview_ready_dsa" in flags and ("github_ghost" in flags or "low_output" in flags):
        flags.append("archetype_theorist")

    # "The Balanced Engineer": Good at both (The Holy Grail)
    elif "proven_impact" in flags and "interview_ready_dsa" in flags:
        flags.append("archetype_top_1_percent")

    # "The Invisible": Bad at both
    elif ("github_ghost" in flags or "tutorial_hell_confirmed" in flags) and (
            "dsa_beginner" in flags or "easy_farmer" in flags):
        flags.append("archetype_invisible")

    # -------------------------
    # ATTACH & RETURN
    # -------------------------
    user_state.evidence_profile = EvidenceProfile(
        github_stats=github_stats if gh_valid else {},
        leetcode_stats=leetcode_stats if lc_valid else {},
        flags=flags
    )

    return user_state