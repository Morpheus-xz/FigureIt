"""
Explanation Bot Demo — FigureIt
Run this file to see how decisions are explained to the user.
"""

import json
from ai_engine.agents.explanation_bot import explain_decision
from ai_engine.models.user_state import (
    UserState,
    BasicProfile,
    ContextProfile,
    Strictness,
    Urgency,
    ProofExpectation,
    EvidenceProfile,
    InterestProfile,
    DecisionState,
    Confidence
)

def run_demo():
    print("\n🔥 RUNNING FIGUREIT EXPLANATION BOT DEMO\n")

    # -------------------------------------------------
    # MOCK USER STATE (Post Decision Engine)
    # -------------------------------------------------

    user = UserState(
        user_id="demo_user",
        basic_profile=BasicProfile(
            college_tier=3,
            year_of_study=3,
            time_availability=6
        )
    )

    user.context_profile = ContextProfile(
        strictness_level=Strictness.HIGH,
        urgency_level=Urgency.MEDIUM,
        max_focus_skills=1,
        proof_expectation=ProofExpectation.STRONG
    )

    user.interest_profile = InterestProfile(
        interest_bias={
            "development": 0.7,
            "problem_solving": 0.8,
            "data": 0.2
        },
        confidence_level=Confidence.HIGH,
        exploration_allowed=False
    )

    user.evidence_profile = EvidenceProfile(
        flags=[
            "projects_show_real_world_signal",
            "dsa_sufficient_for_interviews",
            "dsa_saturation_reached"
        ]
    )

    user.decision_state = DecisionState(
        focus=["Backend Engineering"],
        park=["Frontend Engineering"],
        drop=["Data Science / ML"],
        reasons={}
    )

    # -------------------------------------------------
    # RUN EXPLANATION
    # -------------------------------------------------

    explanation = explain_decision(user)

    print("=== 🧠 SYSTEM EXPLANATION ===\n")
    print(json.dumps(explanation, indent=2))

    print("\n✅ Explanation Demo Complete\n")


if __name__ == "__main__":
    run_demo()
