"""
Explanation Bot — FigureIt (v1.2 PRODUCTION)

ROLE:
- Explain WHY the system made its decisions.
- Translate symbolic evidence into a professional career narrative.
- Build trust by referencing concrete signals (time, evidence, interests).

STRICT RULES:
- NO decision-making
- NO state mutation
- NO chat behavior
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
You are FigureIt, a Senior Career Strategist.

Your task is to explain WHY certain career paths were:
- Focused
- Parked
- Dropped

INPUT SIGNALS:
- Decisions (focus / park / drop)
- Evidence flags (objective signals)
- Time constraints
- User interests

RULES:
1. Always reference evidence or constraints explicitly.
2. Be honest and professional — no motivational fluff.
3. Explain drops clearly (conflict, ROI, time).
4. Keep tone calm, confident, and precise.

OUTPUT STRICT JSON ONLY:
{
  "summary": "1–2 sentence executive summary.",
  "focus_reason": "Why the primary focus was chosen.",
  "park_reason": "Why secondary options were delayed.",
  "drop_reason": "Why some options were eliminated.",
  "time_constraint_note": "How time availability impacted decisions."
}
"""

# =====================================================
# MAIN ENTRY
# =====================================================

def explain_decision(user_state: UserState) -> Dict[str, Any]:
    """
    Generates a human-readable explanation for the DecisionState.
    """

    # ---------- SAFETY CHECK ----------
    if not all([
        user_state.decision_state,
        user_state.evidence_profile,
        user_state.interest_profile,
        user_state.context_profile
    ]):
        return {
            "error": "Incomplete user state. Explanation cannot be generated."
        }

    payload = {
        "decisions": {
            "focus": user_state.decision_state.focus,
            "park": user_state.decision_state.park,
            "drop": user_state.decision_state.drop
        },
        "signals": {
            "evidence_flags": user_state.evidence_profile.flags,
            "primary_interests": [
                k for k, v in user_state.interest_profile.interest_bias.items() if v >= 0.6
            ],
            "weekly_hours": user_state.basic_profile.time_availability,
            "urgency": user_state.context_profile.urgency_level.value
        }
    }

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": json.dumps(payload)}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )

        return json.loads(response.choices[0].message.content)

    except Exception as e:
        print(f"❌ Explanation generation failed: {e}")

        # ---------- SAFE FALLBACK ----------
        return {
            "summary": "We prioritized the path with the strongest evidence and feasibility.",
            "focus_reason": "Your existing skills align best with this direction.",
            "park_reason": "Additional paths were delayed due to focus constraints.",
            "drop_reason": "Some options were removed to avoid low ROI and overload.",
            "time_constraint_note": "Your available weekly time required strict prioritization."
        }
