"""
Override Interpreter Demo — FigureIt
"""

from ai_engine.models.user_state import (
    UserState,
    BasicProfile,
    ContextProfile,
    Strictness,
    Urgency,
    ProofExpectation,
    DecisionState
)

from ai_engine.agents.override_interpreter import interpret_override


def run_demo():
    print("🔥 RUNNING FIGUREIT OVERRIDE INTERPRETER DEMO\n")

    # Mock UserState
    user = UserState(
        user_id="u_demo",
        basic_profile=BasicProfile(
            college_tier=3,
            year_of_study=3,
            time_availability=6
        )
    )

    user.context_profile = ContextProfile(
        strictness_level=Strictness.MEDIUM,
        urgency_level=Urgency.MEDIUM,
        max_focus_skills=1,
        proof_expectation=ProofExpectation.BASIC
    )

    user.decision_state = DecisionState(
        focus=["Backend Engineering"],
        park=["Frontend Engineering"],
        drop=["Data Science / ML"],
        reasons={}
    )

    # User speaks
    user_message = "I want ML even if it’s hard and I can give more time now"

    print("🗣 USER INPUT:")
    print(user_message)

    override = interpret_override(user, user_message)

    print("\n🧠 INTERPRETED CHANGE REQUEST:")
    for k, v in override.items():
        print(f"{k}: {v}")

    print("\n✅ Override Interpreter Demo Complete")


if __name__ == "__main__":
    run_demo()
