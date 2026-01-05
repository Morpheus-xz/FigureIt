"""
Panic Bot — FigureIt (v2.0 FINAL + MARKET AWARE)

ROLE:
- Emotional stabilizer
- Helps user regain clarity during stress or overwhelm
- References market pressure WITHOUT fear-mongering

IMPORTANT:
- NEVER changes decisions
- NEVER suggests new paths
- NEVER gives technical advice
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
You are a calm, grounded mentor helping a stressed user.

GOALS:
- Reduce anxiety
- Restore a sense of control
- Normalize market pressure without fear

RULES:
- Do NOT suggest changing career paths
- Do NOT give technical plans
- Do NOT deny market reality
- Frame competition as manageable, not threatening

STRUCTURE YOUR RESPONSE INTO THESE SECTIONS:
- EMPATHY
- REALITY_CHECK
- REFRAME
- NEXT_STEP
- CONTROL_NOTE

Tone:
- Calm
- Reassuring
- Grounded
- Non-judgmental

Output STRICT JSON only.
"""

# =====================================================
# MAIN HANDLER
# =====================================================

def handle_panic(user_state: UserState, message: str) -> Dict[str, Any]:
    """
    Handles panic/anxiety messages.
    Market-aware but emotionally safe.
    """

    # -------------------------
    # 1. BASIC SAFETY CHECK
    # -------------------------

    if not user_state.decision_state:
        return {
            "error": "Decision state missing. Panic bot requires an existing decision."
        }

    # -------------------------
    # 2. EXTRACT CONTEXT
    # -------------------------

    focus = user_state.decision_state.focus[0]
    hours = user_state.basic_profile.time_availability
    urgency = user_state.context_profile.urgency_level.name

    # -------------------------
    # 3. MARKET CONTEXT (SUPPORTING ONLY)
    # -------------------------

    market = MarketPulse(client=client)

    # Map focus → representative skill
    focus_skill_map = {
        "Frontend Engineering": "React",
        "Backend Engineering": "Python",
        "Data Science / ML": "Python",
        "Competitive Programming": "Algorithms"
    }

    skill = focus_skill_map.get(focus)
    market_info = {}

    if skill:
        snapshot = market.snapshot()["skills"].get(skill, {})
        market_info = {
            "trend": snapshot.get("trend", "stable"),
            "saturation": snapshot.get("saturation", "medium")
        }

    # -------------------------
    # 4. BUILD LLM PAYLOAD
    # -------------------------

    payload = {
        "user_message": message,
        "current_focus": focus,
        "time_per_week": hours,
        "urgency": urgency,
        "market_context": market_info
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
            temperature=0.3
        )

        raw = response.choices[0].message.content.strip()

        # Strict JSON extraction
        start = raw.find("{")
        end = raw.rfind("}") + 1
        result = json.loads(raw[start:end])

        return result

    except Exception as e:
        print(f"❌ Panic bot failed: {e}")
        return _fallback_panic_response(focus)

# =====================================================
# FALLBACK RESPONSE
# =====================================================

def _fallback_panic_response(focus: str) -> Dict[str, Any]:
    """
    Safe fallback if LLM fails.
    """
    return {
        "EMPATHY": "Feeling overwhelmed is normal, especially when you're taking your goals seriously.",
        "REALITY_CHECK": "The market is competitive, but competition does not mean impossibility.",
        "REFRAME": f"You are already on a focused path ({focus}), which reduces noise and increases clarity.",
        "NEXT_STEP": "Take 10 minutes and write down one small task you can complete today.",
        "CONTROL_NOTE": "You are not locked in forever. Every step you take gives you more options, not fewer."
    }
