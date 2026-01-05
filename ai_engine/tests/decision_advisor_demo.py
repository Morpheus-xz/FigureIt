"""
Decision Advisor Demo — FigureIt (v1.0)

PURPOSE:
- Test Decision Advisor in isolation
- Uses Decision Engine output
- No Orchestrator
"""

from dotenv import load_dotenv
load_dotenv()

# -------------------------------
# IMPORT MODELS
# -------------------------------
from ai_engine.models.user_state import (
    UserState,
    BasicProfile,
    ContextProfile,
    EvidenceProfile,
    InterestProfile,
    Strictness,
    Urgency,
    ProofExpectation,
    Confidence
)

# -------------------------------
# IMPORT AGENTS
# -------------------------------
from ai_engine.market.market_pulse import MarketPulse
from ai_engine.agents.decision_engine import make_decision
from ai_engine.agents.decision_advisor import advise_decision

from openai import OpenAI
import os


def run_demo():
    print("🔥 RUNNING DECISION ADVISOR DEMO\n")

    # -------------------------------
    # 1. USER STATE
    # -------------------------------
    user = UserState(
        user_id="advisor_demo_user",
        basic_profile=BasicProfile(
            college_tier=3,
            year_of_study=3,
            time_availability=6,
            constraints=[]
        )
    )

    # -------------------------------
    # 2. CONTEXT (FIXED)
    # -------------------------------
    user.context_profile = ContextProfile(
        strictness_level=Strictness.HIGH,
        urgency_level=Urgency.MEDIUM,
        max_focus_skills=1,
        proof_expectation=ProofExpectation.BASIC  # ✅ REQUIRED
    )

    # -------------------------------
    # 3. EVIDENCE
    # -------------------------------
    user.evidence_profile = EvidenceProfile(
        github_stats={
            "repos": 12,
            "stars": 8,
            "top_lang": "Python"
        },
        leetcode_stats={
            "total_solved": 340,
            "easy": 140,
            "medium": 180,
            "hard": 20
        },
        flags=[]
    )

    # -------------------------------
    # 4. INTERESTS
    # -------------------------------
    user.interest_profile = InterestProfile(
        interest_bias={
            "development": 0.9,
            "problem_solving": 0.8,
            "data": 0.4
        },
        confidence_level=Confidence.HIGH,
        exploration_allowed=False
    )

    # -------------------------------
    # 5. MARKET + DECISION
    # -------------------------------
    market = MarketPulse(
        client=OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    )

    user = make_decision(user, market)

    # -------------------------------
    # 6. DECISION ADVISOR
    # -------------------------------
    advice = advise_decision(user)

    # -------------------------------
    # 7. OUTPUT
    # -------------------------------
    print("🧠 DECISION ADVISOR OUTPUT\n")

    for k, v in advice.items():
        print(f"{k.upper()}:\n{v}\n")

    print("✅ Decision Advisor Demo Complete\n")


if __name__ == "__main__":
    run_demo()
