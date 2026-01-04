"""
Multi-User Simulation — FigureIt

Purpose:
- Prove that same AI code works for multiple users
- Each user has an independent UserState
- Each produces different InterestProfiles
"""

from ai_engine.models.user_state import UserState, BasicProfile
from ai_engine.agents.interest_chatbot import (
    analyze_interests,
    DISCOVERY_QUESTIONS
)


def run_multi_user_demo():
    print("\n=== MULTI USER DEMO ===\n")

    # -----------------------
    # USER 1 (Logic + Data)
    # -----------------------
    user1 = UserState(
        user_id="user_logic",
        basic_profile=BasicProfile(
            college_tier=3,
            year_of_study=2,
            time_availability=12
        )
    )

    answers_user1 = {
        DISCOVERY_QUESTIONS[0]: "Solving logic puzzles. I hate UI work.",
        DISCOVERY_QUESTIONS[1]: "Curiosity. I enjoy debugging.",
        DISCOVERY_QUESTIONS[2]: "Abstract patterns, math and data.",
        DISCOVERY_QUESTIONS[3]: "Frontend because styling bored me."
    }

    user1 = analyze_interests(user1, answers_user1)

    # -----------------------
    # USER 2 (Frontend / Product)
    # -----------------------
    user2 = UserState(
        user_id="user_builder",
        basic_profile=BasicProfile(
            college_tier=2,
            year_of_study=3,
            time_availability=8
        )
    )

    answers_user2 = {
        DISCOVERY_QUESTIONS[0]: "Building interfaces and seeing visual output.",
        DISCOVERY_QUESTIONS[1]: "Frustration. Bugs annoy me.",
        DISCOVERY_QUESTIONS[2]: "Tangible things like apps and websites.",
        DISCOVERY_QUESTIONS[3]: "I quit competitive programming. Too abstract."
    }

    user2 = analyze_interests(user2, answers_user2)

    # -----------------------
    # RESULTS
    # -----------------------
    print("USER 1 RESULT:")
    print(user1.interest_profile)

    print("\nUSER 2 RESULT:")
    print(user2.interest_profile)


if __name__ == "__main__":
    run_multi_user_demo()
