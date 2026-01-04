"""
Panic Bot — FigureIt (v1.1 CONTEXT-AWARE)

ROLE:
- Crisis Coach.
- Detects the SOURCE of panic (urgency, skill gap, burnout).
- Reframes anxiety into a tactical pause.
- Stabilizes without mutating decisions.

INPUT: UserState + User Message
OUTPUT: JSON Stabilization Plan
"""

import os
import json
from typing import Dict, Any
from dotenv import load_dotenv
from openai import OpenAI

from ai_engine.models.user_state import UserState

# =====================================================
# CONFIG
# =====================================================

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# =====================================================
# SYSTEM PROMPT
# =====================================================

SYSTEM_PROMPT = """
You are FigureIt’s Crisis Coach.
The user is overwhelmed, confused, or anxious.

Your goal is to perform a Tactical Reset.

INPUT DATA YOU WILL RECEIVE:
- Focus Path
- Urgency Level
- Evidence Flags
- Weekly Time Availability
- User Message

RULES:
1. Validate, do not pity.
2. Use context to explain WHY the stress exists.
3. Reframe panic as a signal to focus, not quit.
4. Suggest ONE extremely small next step (5 minutes).
5. Reinforce that all decisions are reversible.

OUTPUT STRICT JSON ONLY:
{
  "empathy": "Direct validation of the specific stressor.",
  "reframe": "Why this feeling is actually a signal to focus, not quit.",
  "clarification": "Simplified explanation of the system’s current goal.",
  "next_step": "A 5-minute atomic action to break paralysis.",
  "control_note": "Reminder that the user is always in control."
}
"""

# =====================================================
# MAIN ENTRY
# =====================================================

def handle_panic(user_state: UserState, user_message: str) -> Dict[str, Any]:
    """
    Generates a context-aware stabilization response.
    """

    payload = {
        "user_message": user_message,
        "context": {
            "focus_path": (
                user_state.decision_state.focus[0]
                if user_state.decision_state and user_state.decision_state.focus
                else "None"
            ),
            "urgency": (
                user_state.context_profile.urgency_level.name
                if user_state.context_profile
                else "UNKNOWN"
            ),
            "weekly_hours": user_state.basic_profile.time_availability,
            "evidence_flags": (
                user_state.evidence_profile.flags
                if user_state.evidence_profile
                else []
            )
        }
    }

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": json.dumps(payload)}
            ],
            temperature=0.4,
            response_format={"type": "json_object"}
        )

        return json.loads(response.choices[0].message.content)

    except Exception:
        # Hard fallback — NO LLM dependency
        return {
            "empathy": "This feels heavy because there are real constraints involved.",
            "reframe": "That pressure means the system is narrowing focus, not blocking you.",
            "clarification": "Right now, the goal is to make one path manageable within your time.",
            "next_step": "Open your roadmap and read just the first task. Nothing else.",
            "control_note": "You can pause, override, or change direction at any time."
        }
