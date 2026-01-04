from ai_engine.agents.panic_bot import handle_panic
from ai_engine.models.user_state import (
    UserState,
    BasicProfile,
    ContextProfile,
    Strictness,
    Urgency,
    ProofExpectation,
    DecisionState,
    EvidenceProfile
)

def run_demo():
    print("🔥 RUNNING FIGUREIT PANIC BOT DEMO\n")

    user = UserState(
        user_id="panic_test_user",
        basic_profile=BasicProfile(
            college_tier=3,
            year_of_study=4,
            time_availability=5
        )
    )

    user.context_profile = ContextProfile(
        strictness_level=Strictness.HIGH,
        urgency_level=Urgency.HIGH,
        max_focus_skills=1,
        proof_expectation=ProofExpectation.STRONG
    )

    user.decision_state = DecisionState(
        focus=["Backend Engineering"],
        park=["Frontend Engineering"],
        drop=["Data Science / ML"]
    )

    user.evidence_profile = EvidenceProfile(
        flags=["weak_dsa_foundation", "portfolio_needs_polish"]
    )

    user_message = "I feel completely stuck and I don’t know if I’m good enough"

    response = handle_panic(user, user_message)

    print("🧠 PANIC BOT RESPONSE:\n")
    for key, value in response.items():
        print(f"{key.upper()}: {value}")

    print("\n✅ Panic Bot Demo Complete")

if __name__ == "__main__":
    run_demo()
