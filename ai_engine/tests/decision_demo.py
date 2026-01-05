"""
Decision Advisor Demo — FigureIt

Tests the advisory layer on top of Decision Engine output
"""

from dotenv import load_dotenv
load_dotenv()

from ai_engine.models.user_state import (
    UserState,
    BasicProfile,
    ContextProfile,
    EvidenceProfile,
    InterestProfile,
    DecisionState,
    Strictness,
    Urgency,
    ProofExpectation,
    Confidence
)

from ai_engine.agents.decision_advisor import advise_decision

def run_demo():
    print("🔥 RUNNING DECISION ADVISOR DEMO\n")

    # -------------------------------
    # MOCK USER STATE (Post-Decision)
    # -------------------------------
    user = UserState(
        user_id="advisor_demo",
        basic_profile=BasicProfile(
            college_tier=3,
            year_of_study=3,
            time_availability=6,
            constraints=[]
        )
    )

    user.context_profile = ContextProfile(
        strictness_level=Strictness.HIGH,
        urgency_level=Urgency.MEDIUM,
        max_focus_skills=1,
        proof_expectation=ProofExpectation.BASIC
    )

    user.evidence_profile = EvidenceProfile(
        github_stats={"repos": 12, "stars": 8},
        leetcode_stats={"total_solved": 340, "medium": 180},
        flags=[]
    )

    user.interest_profile = InterestProfile(
        interest_bias={
            "development": 0.9,
            "problem_solving": 0.8,
            "data": 0.4
        },
        confidence_level=Confidence.HIGH,
        exploration_allowed=False
    )

    user.decision_state = DecisionState(
        focus=["Frontend Engineering"],
        park=["Backend Engineering"],
        drop=["Data Science / ML"],
        reasons={
            "Frontend Engineering": "Best alignment score (0.61)",
            "Backend Engineering": "Good but bandwidth limited",
            "Data Science / ML": "Low ROI"
        }
    )

    # -------------------------------
    # RUN ADVISOR
    # -------------------------------
    advice = advise_decision(user)

    print("🧠 DECISION ADVISOR OUTPUT\n")
    for k, v in advice.items():
        print(f"{k.upper()}:")
        print(v)
        print()

    print("✅ Decision Advisor Demo Complete\n")

if __name__ == "__main__":
    run_demo()
