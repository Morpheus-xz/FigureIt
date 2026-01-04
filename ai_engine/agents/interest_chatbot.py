"""
Interest Discovery Agent (v1) — FigureIt
"""

import os
import json
from typing import Dict
from dotenv import load_dotenv
from openai import OpenAI

from ai_engine.models.user_state import (
    UserState,
    InterestProfile,
    Confidence
)

# =====================================================
# ENV & CLIENT SETUP
# =====================================================

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY missing")

client = OpenAI(api_key=OPENAI_API_KEY)

# =====================================================
# QUESTIONS
# =====================================================

DISCOVERY_QUESTIONS = [
    "Which activity makes time pass faster for you: building interfaces or solving logic problems?",
    "When debugging, do you feel more frustration or curiosity?",
    "Do you prefer tangible outputs (apps/websites) or abstract patterns (math/data)?",
    "What is one technical thing you tried learning but quit? Why?"
]

# =====================================================
# LLM EXTRACTION
# =====================================================

def _extract_interest_signals(answers: Dict[str, str]) -> Dict[str, float]:
    system_prompt = """
You are a JSON-only interest signal extractor.

Rules:
- Output ONLY valid JSON
- No explanations
- No markdown
- Values must be between 0.0 and 1.0

Output format:
{
  "development": number,
  "problem_solving": number,
  "data": number
}
"""

    payload = json.dumps(answers, indent=2)

    try:
        response = client.responses.create(
            model="gpt-4o-mini",
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": payload}
            ],
            temperature=0.0,
            max_output_tokens=150
        )

        text = response.output_text.strip()

        start = text.find("{")
        end = text.rfind("}") + 1
        raw = json.loads(text[start:end])

        return {
            "development": float(raw["development"]),
            "problem_solving": float(raw["problem_solving"]),
            "data": float(raw["data"])
        }

    except Exception:
        return {"development": 0.3, "problem_solving": 0.3, "data": 0.3}

# =====================================================
# MAIN ENTRY
# =====================================================

def analyze_interests(user_state: UserState, answers: Dict[str, str]) -> UserState:
    if user_state.interest_profile is not None:
        return user_state

    bias = _extract_interest_signals(answers)
    max_signal = max(bias.values())

    if max_signal >= 0.7:
        confidence = Confidence.HIGH
    elif max_signal <= 0.4:
        confidence = Confidence.LOW
    else:
        confidence = Confidence.MEDIUM

    user_state.interest_profile = InterestProfile(
        interest_bias=bias,
        confidence_level=confidence,
        exploration_allowed=confidence != Confidence.HIGH
    )

    return user_state

# =====================================================
# TEST
# =====================================================

if __name__ == "__main__":
    from ai_engine.models.user_state import BasicProfile

    user = UserState(
        user_id="test_user",
        basic_profile=BasicProfile(3, 2, 10)
    )

    answers = {
        DISCOVERY_QUESTIONS[0]: "Solving logic puzzles. I dislike CSS.",
        DISCOVERY_QUESTIONS[1]: "Curiosity.",
        DISCOVERY_QUESTIONS[2]: "Abstract patterns, math.",
        DISCOVERY_QUESTIONS[3]: "Frontend bored me."
    }

    updated = analyze_interests(user, answers)
    print(updated.interest_profile)
