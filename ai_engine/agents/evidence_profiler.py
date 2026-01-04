"""
Evidence Profiler Agent — FigureIt (v2.4 FINAL)

ROLE:
- Convert raw GitHub & LeetCode data into ACTIONABLE, PROFESSIONAL signals.
- Identify leverage points, inefficiencies, and readiness states.
- Feed clean evidence into the Decision Engine (FOCUS / PARK / DROP).

PRINCIPLES:
- No rankings
- No ego labels
- No "Top X%" language
- Signals must directly imply next actions
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from ai_engine.models.user_state import UserState, EvidenceProfile


# =====================================================
# THRESHOLDS (TUNABLE, EXPLICIT)
# =====================================================

THRESHOLDS = {
    # GitHub
    "MIN_REPOS": 3,
    "IMPACT_STARS": 5,                 # External validation exists
    "PORTFOLIO_POLISH_STARS": 10,      # Strong quality signal
    "STALE_ACCOUNT_YEARS": 2,          # Long inactivity

    # DSA
    "DSA_BEGINNER_LIMIT": 15,
    "INTERVIEW_READY_MEDIUMS": 40,
    "DSA_SATURATION_TOTAL": 200,       # Generic grinding loses ROI
    "LOW_DIFFICULTY_RATIO": 0.7        # Too many Easy problems
}


# =====================================================
# HELPERS
# =====================================================

def _calculate_account_age(created_at: str) -> float:
    if not created_at:
        return 0.0
    try:
        start = datetime.strptime(created_at, "%Y-%m-%d")
        return (datetime.now() - start).days / 365.0
    except Exception:
        return 0.0


# =====================================================
# MAIN AGENT
# =====================================================

def build_evidence(
    user_state: UserState,
    github_stats: Optional[Dict[str, Any]],
    leetcode_stats: Optional[Dict[str, Any]]
) -> UserState:
    """
    Builds EvidenceProfile focused on readiness and leverage,
    NOT on ranking or comparison.
    """

    flags: List[str] = []

    # -------------------------------------------------
    # 1. GITHUB ANALYSIS — IMPLEMENTATION SIGNAL
    # -------------------------------------------------

    gh_valid = github_stats and github_stats.get("valid")

    if not gh_valid:
        flags.append("no_project_evidence")
        repo_count = 0
        stars = 0
        account_age = 0.0
    else:
        repo_count = github_stats.get("repos", 0)
        stars = github_stats.get("stars", 0)
        account_age = _calculate_account_age(
            github_stats.get("account_created", "")
        )

        if repo_count < THRESHOLDS["MIN_REPOS"]:
            flags.append("early_stage_projects")

        if stars >= THRESHOLDS["IMPACT_STARS"]:
            flags.append("projects_show_real_world_signal")

        if stars < THRESHOLDS["PORTFOLIO_POLISH_STARS"] and repo_count >= 5:
            flags.append("portfolio_needs_polish")

        if account_age > THRESHOLDS["STALE_ACCOUNT_YEARS"] and repo_count < 5:
            flags.append("stagnant_project_growth")

    # -------------------------------------------------
    # 2. LEETCODE ANALYSIS — PROBLEM SOLVING SIGNAL
    # -------------------------------------------------

    lc_valid = leetcode_stats and leetcode_stats.get("valid")

    if not lc_valid:
        flags.append("no_dsa_evidence")
        total = easy = medium = hard = 0
    else:
        total = leetcode_stats.get("total_solved", 0)
        easy = leetcode_stats.get("easy", 0)
        medium = leetcode_stats.get("medium", 0)
        hard = leetcode_stats.get("hard", 0)

        if total < THRESHOLDS["DSA_BEGINNER_LIMIT"]:
            flags.append("weak_dsa_foundation")

        if medium >= THRESHOLDS["INTERVIEW_READY_MEDIUMS"]:
            flags.append("dsa_sufficient_for_interviews")

        if total >= THRESHOLDS["DSA_SATURATION_TOTAL"]:
            flags.append("dsa_saturation_reached")

        if total > 50:
            if (easy / total) > THRESHOLDS["LOW_DIFFICULTY_RATIO"]:
                flags.append("low_difficulty_bias")

    # -------------------------------------------------
    # 3. CROSS-SIGNAL INSIGHTS — THE IMPORTANT PART
    # -------------------------------------------------

    # Strong DSA, weak projects → shift to building
    if (
        "dsa_saturation_reached" in flags
        and "portfolio_needs_polish" in flags
    ):
        flags.append("shift_focus_to_projects")

    # Strong projects, weak DSA → strengthen fundamentals
    if (
        "projects_show_real_world_signal" in flags
        and "weak_dsa_foundation" in flags
    ):
        flags.append("strengthen_core_dsa")

    # Strong both → execution phase
    if (
        "projects_show_real_world_signal" in flags
        and "dsa_sufficient_for_interviews" in flags
    ):
        flags.append("execution_ready_profile")

    # -------------------------------------------------
    # ATTACH & RETURN
    # -------------------------------------------------

    user_state.evidence_profile = EvidenceProfile(
        github_stats=github_stats if gh_valid else {},
        leetcode_stats=leetcode_stats if lc_valid else {},
        flags=flags
    )

    return user_state
