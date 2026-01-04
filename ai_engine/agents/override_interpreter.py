"""
Override Interpreter — FigureIt (v1.2.1 FINAL)

ROLE:
- Interpret user intent (natural language).
- Convert vague phrases into STRICT system constraints.
- Return a Change Request object (NO state mutation).
"""

from typing import Dict, Any
import json
import os
from dotenv import load_dotenv
from openai import OpenAI

from ai_engine.models.user_state import UserState

# =====================================================
# CONFIG
# =====================================================

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# =====================================================
# ALLOWED SYSTEM KEYS
# =====================================================

ALLOWED_PATHS = [
    "Frontend Engineering",
    "Backend Engineering",
    "Data Science / ML",
    "Competitive Programming"
]

# =====================================================
# SYSTEM PROMPT (FIXED)
# =====================================================

SYSTEM_PROMPT = f"""
You are the Control Interface for a Career AI system.

VALID CAREER PATHS (USE EXACT STRINGS ONLY):
{json.dumps(ALLOWED_PATHS)}

YOUR JOB:
- Convert user intent into STRICT system constraints.
- NEVER invent new career paths.
- NEVER explain anything outside the JSON.

DETECTION RULES:
1. Map vague careers:
   - "web dev" → "Frontend Engineering"
   - "backend" → "Backend Engineering"
   - "ml" / "ai" / "data" → "Data Science / ML"
   - "coding problems" → "Competitive Programming"

2. Time signals:
   - "more time", "freer", "can grind" → increase hours
   - "busy", "less time" → decrease hours

3. Urgency signals:
   - "job now", "urgent", "placement" → high
   - "exploring", "no rush" → low

OUTPUT STRICT JSON ONLY:
{{
  "hours_per_week": null,
  "urgency": "low" | "medium" | "high" | null,
  "force_include": [],
  "force_exclude": [],
  "exploration_allowed": null,
  "reason": "short explanation"
}}
"""

# =====================================================
# MAIN ENTRY
# =====================================================

def interpret_override(
    user_state: UserState,
    user_message: str
) -> Dict[str, Any]:
    """
    Interprets user intent and returns a structured override request.
    """

    payload = {
        "current_state": {
            "hours_per_week": user_state.basic_profile.time_availability,
            "urgency": (
                user_state.context_profile.urgency_level.name.lower()
                if user_state.context_profile else "unknown"
            ),
            "current_focus": (
                user_state.decision_state.focus
                if user_state.decision_state else []
            )
        },
        "user_input": user_message
    }

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": json.dumps(payload)}
            ],
            temperature=0.0,
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)

        # -------------------------
        # SAFETY FILTER
        # -------------------------
        valid = set(ALLOWED_PATHS)

        result["force_include"] = [
            p for p in result.get("force_include", []) if p in valid
        ]

        result["force_exclude"] = [
            p for p in result.get("force_exclude", []) if p in valid
        ]

        return result

    except Exception as e:
        print(f"❌ Override interpretation failed: {e}")
        return {
            "hours_per_week": None,
            "urgency": None,
            "force_include": [],
            "force_exclude": [],
            "exploration_allowed": None,
            "reason": "Failed to interpret user intent."
        }
