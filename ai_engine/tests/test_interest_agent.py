from ai_engine.models.user_state import UserState, BasicProfile
from ai_engine.agents.interest_chatbot import (
    analyze_interests,
    DISCOVERY_QUESTIONS
)

def talk_to_interest_agent():
    print("\n=== FigureIt: Interest Discovery Test ===\n")

    # Step 1: Create user
    user = UserState(
        user_id="test_user_001",
        basic_profile=BasicProfile(
            college_tier=3,
            year_of_study=2,
            time_availability=12
        )
    )

    # Step 2: Ask questions like a chatbot
    answers = {}
    for q in DISCOVERY_QUESTIONS:
        print("AI:", q)
        ans = input("You: ")
        answers[q] = ans
        print()

    # Step 3: Run agent
    updated_user = analyze_interests(user, answers)

    # Step 4: Show result
    print("\n=== AI UNDERSTANDING ===")
    print("Interest Bias:", updated_user.interest_profile.interest_bias)
    print("Confidence:", updated_user.interest_profile.confidence_level.value)
    print("Exploration Allowed:", updated_user.interest_profile.exploration_allowed)


if __name__ == "__main__":
    talk_to_interest_agent()
