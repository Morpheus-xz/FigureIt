"""
Explanation Bot — FigureIt (v2.0 FINAL + MARKET AWARE)

ROLE:
- Explains WHY decisions were made
- Converts numeric + market signals into human-readable reasoning
- Read-only agent (NO state mutation)

IMPORTANT:
- NEVER changes decisions
- NEVER suggests new paths
- Uses market context only as supporting evidence
"""

import os
import json
from typing import Dict, Any
from dotenv import load_dotenv
from openai import OpenAI

from ai_engine.models.user_state import UserState
from ai_engine.market.market_pulse import MarketPulse

# =====================================================
# ENV SETUP
# =====================================================

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# =====================================================
# SYSTEM PROMPT
# =====================================================

SYSTEM_PROMPT = """
You are a senior career advisor explaining an already-made decision.

You are NOT deciding anything.
You are ONLY explaining.

INPUTS:
- User Evidence Summary
- User Interests
- Context Constraints
- Decision Outcome (focus / park / drop)
- Market Context (trend & saturation)

RULES:
- Be factual, calm, and confidence-building
- Explain trade-offs clearly
- Do NOT suggest changing paths
- Do NOT give step-by-step plans
- Output STRICT JSON ONLY

OUTPUT FORMAT:
{
  "summary": "string",
  "focus_reason": "string",
  "park_reason": "string",
  "drop_reason": "string",
  "time_constraint_note": "string"
}
"""

# =====================================================
# MAIN FUNCTION
# =====================================================

def explain_decision(user_state: UserState) -> Dict[str, Any]:
    """
    Generates a human-readable explanation of the decision.
    Market-aware, JSON-safe, production-ready.
    """

    if not user_state.decision_state:
        return {"error": "Decision state missing."}

    # -------------------------
    # 1. EXTRACT DECISION DATA
    # -------------------------

    focus = user_state.decision_state.focus
    park = user_state.decision_state.park
    drop = user_state.decision_state.drop
    reasons = user_state.decision_state.reasons

    # -------------------------
    # 2. EVIDENCE SUMMARY
    # -------------------------

    evidence_summary = {
        "projects": user_state.evidence_profile.github_stats if user_state.evidence_profile else {},
        "dsa": user_state.evidence_profile.leetcode_stats if user_state.evidence_profile else {},
        "flags": user_state.evidence_profile.flags if user_state.evidence_profile else []
    }

    interests = (
        user_state.interest_profile.interest_bias
        if user_state.interest_profile
        else {}
    )

    context = {
        "time_per_week": user_state.basic_profile.time_availability,
        "urgency": user_state.context_profile.urgency_level.name,
        "strictness": user_state.context_profile.strictness_level.name
    }

    # -------------------------
    # 3. MARKET CONTEXT (READ ONLY)
    # -------------------------

    market = MarketPulse(client=client)

    focus_skill_map = {
        "Frontend Engineering": "React",
        "Backend Engineering": "Python",
        "Data Science / ML": "Python",
        "Competitive Programming": "Algorithms"
    }

    market_context = {}
    for path in focus + park + drop:
        skill = focus_skill_map.get(path)
        if skill:
            snapshot = market.snapshot()["skills"].get(skill, {})
            market_context[path] = {
                "trend": snapshot.get("trend", "stable"),
                "saturation": snapshot.get("saturation", "medium")
            }

    # -------------------------
    # 4. BUILD LLM PAYLOAD
    # -------------------------

    payload = {
        "focus": focus,
        "park": park,
        "drop": drop,
        "decision_reasons": reasons,
        "evidence_summary": evidence_summary,
        "interests": interests,
        "context": context,
        "market_context": market_context
    }

    # -------------------------
    # 5. LLM CALL
    # -------------------------

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": json.dumps(payload)}
            ],
            temperature=0.2
        )

        raw = response.choices[0].message.content.strip()

        # Strict JSON extraction
        start = raw.find("{")
        end = raw.rfind("}") + 1
        explanation = json.loads(raw[start:end])

        return explanation

    except Exception as e:
        print(f"❌ Explanation generation failed: {e}")
        return _fallback_explanation(focus, park, drop)

# =====================================================
# FALLBACK
# =====================================================

def _fallback_explanation(focus, park, drop) -> Dict[str, Any]:
    """
    Safe fallback explanation (no LLM).
    """
    return {
        "summary": "The decision was made based on your strongest evidence signals, interests, and available time.",
        "focus_reason": f"{focus[0]} aligns best with your current profile and constraints.",
        "park_reason": f"{', '.join(park)} remain viable but are deprioritized due to focus limits.",
        "drop_reason": f"{', '.join(drop)} show lower short-term return given current constraints.",
        "time_constraint_note": "Limited weekly time required a focused approach."
    }
