"""
Decision Advisor — FigureIt (v1.0 FINAL)

ROLE:
- Strategic consultant layered ABOVE the Decision Engine
- Explains tradeoffs, risks, and improvement paths
- NEVER mutates state
- NEVER overrides the Decision Engine

INPUT:
- UserState (read-only)

OUTPUT:
- Advisory JSON (human-facing)
"""

import json
import os
from typing import Dict, Any
from dotenv import load_dotenv
from openai import OpenAI

from ai_engine.models.user_state import UserState

# -------------------------------------------------
# ENV + CLIENT
# -------------------------------------------------
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# -------------------------------------------------
# SYSTEM PROMPT
# -------------------------------------------------

SYSTEM_PROMPT = """
You are a Senior Career Strategy Advisor.

You are NOT deciding careers.
The Decision Engine has already decided using math + market data.

Your task:
- Explain WHY the top path wins
- Explain WHY other paths lost
- Suggest WHAT to improve if the user wants to switch paths

RULES:
- Be factual and grounded in evidence
- No motivation fluff
- No new decisions
- No rankings

OUTPUT STRICT JSON ONLY:

{
  "primary_focus_analysis": "Why this path is optimal right now",
  "risk_notes": ["specific risk 1", "specific risk 2"],
  "parked_path_guidance": {
    "<path>": "what to improve to make this viable"
  },
  "dropped_path_warning": {
    "<path>": "why this is currently a bad bet"
  },
  "what_to_do_next": ["concrete next actions"]
}
"""

# -------------------------------------------------
# MAIN ENTRY
# -------------------------------------------------

def advise_decision(user_state: UserState) -> Dict[str, Any]:
    """
    Produces strategic advice on top of an existing decision.
    """

    if not user_state.decision_state:
        return {"error": "DecisionState missing. Run Decision Engine first."}

    payload = {
        "decision": {
            "focus": user_state.decision_state.focus,
            "park": user_state.decision_state.park,
            "drop": user_state.decision_state.drop,
            "reasons": user_state.decision_state.reasons
        },
        "evidence": {
            "github": user_state.evidence_profile.github_stats,
            "leetcode": user_state.evidence_profile.leetcode_stats
        },
        "interests": user_state.interest_profile.interest_bias,
        "context": {
            "hours_per_week": user_state.basic_profile.time_availability,
            "urgency": user_state.context_profile.urgency_level.name
        }
    }

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": json.dumps(payload)}
            ],
            temperature=0.25,
            response_format={"type": "json_object"}
        )

        return json.loads(response.choices[0].message.content)

    except Exception as e:
        return {
            "error": "Decision advisor failed",
            "details": str(e)
        }
