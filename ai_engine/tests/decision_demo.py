"""
Decision Engine Demo — FigureIt

Purpose:
- Human-readable test for Decision Engine
- Shows WHY a path was chosen
- Same style as evidence_demo.py
"""

from ai_engine.models.user_state import (
    UserState, BasicProfile,
    ContextProfile, Strictness, Urgency, ProofExpectation,
    EvidenceProfile, InterestProfile, Confidence
)
from ai_engine.agents.decision_engine import make_decision


def run_demo():
    print("\n🔥 RUNNING FIGUREIT DECISION ENGINE DEMO\n")

    # -----------------------------------------
    # SIMULATED USER (Realistic Profile)
    # -----------------------------------------
    user = UserState(
        user_id="demo_user",
        basic_profile=BasicProfile(
            college_tier=3,
            year_of_study=2,
            time_availability=8   # Limited time
        )
    )

    user.context_profile = ContextProfile(
        strictness_level=Strictness.HIGH,
        urgency_level=Urgency.MEDIUM,
        max_focus_skills=1,
        proof_expectation=ProofExpectation.BASIC
    )

    user.interest_profile = InterestProfile(
        interest_bias={
            "development": 0.6,
            "problem_solving": 0.8,
            "data": 0.2
        },
        confidence_level=Confidence.HIGH,
        exploration_allowed=False
    )

    user.evidence_profile = EvidenceProfile(
        github_stats={
            "repos": 14,
            "stars": 14,
            "top_lang": "Python"
        },
        leetcode_stats={
            "total_solved": 332,
            "easy": 152,
            "medium": 165,
            "hard": 15
        },
        flags=[
            "projects_show_real_world_signal",
            "dsa_sufficient_for_interviews",
            "dsa_saturation_reached",
            "execution_ready_profile"
        ]
    )

    # -----------------------------------------
    # RUN DECISION ENGINE
    # -----------------------------------------
    user = make_decision(user)

    # -----------------------------------------
    # OUTPUT (HUMAN READABLE)
    # -----------------------------------------
    print("=== 🎯 FINAL DECISION ===\n")

    print("FOCUS:")
    for f in user.decision_state.focus:
        print(f"  ✔ {f}")

    print("\nPARK:")
    for p in user.decision_state.park:
        print(f"  ⏸ {p}")

    print("\nDROP:")
    for d in user.decision_state.drop:
        print(f"  ✖ {d}")

    print("\n=== 🧠 REASONS ===")
    for path, reason in user.decision_state.reasons.items():
        print(f"- {path}: {reason}")

    print("\n✅ Decision Demo Complete\n")


if __name__ == "__main__":
    run_demo()
