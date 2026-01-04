from ai_engine.models.user_state import UserState, BasicProfile
from ai_engine.agents.context_profiler import build_context
from ai_engine.models.user_state import Strictness, Urgency, ProofExpectation


def test_context_profiler_high_strictness():
    user = UserState(
        user_id="pytest_user",
        basic_profile=BasicProfile(
            college_tier=3,
            year_of_study=3,
            time_availability=8
        )
    )

    user = build_context(user)

    assert user.context_profile is not None
    assert user.context_profile.strictness_level == Strictness.HIGH
    assert user.context_profile.urgency_level == Urgency.MEDIUM
    assert user.context_profile.max_focus_skills == 1
    assert user.context_profile.proof_expectation == ProofExpectation.STRONG
