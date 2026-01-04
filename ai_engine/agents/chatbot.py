"""
FigureIt Chatbot — v1.1 (Pedagogically Adaptive)

ROLE:
- The "Front Desk" for the AI Brain.
- Routes intents (Panic, Override) to the Orchestrator.
- Handles 'Learning' queries with an ADAPTIVE TUTOR.
- Uses Evidence Flags to decide if the user needs 'Theory' or 'Code'.

This chatbot NEVER mutates UserState directly.
"""

import json
import os
from typing import Dict, Any
from dotenv import load_dotenv
from openai import OpenAI

# Models & Logic
from ai_engine.models.user_state import UserState
from ai_engine.orchestrator import Orchestrator

# Direct Agent Imports (for read-only access)
from ai_engine.agents.explanation_bot import explain_decision
from ai_engine.agents.roadmap_generator import generate_roadmap

# =====================================================
# CONFIG
# =====================================================

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
orchestrator = Orchestrator()

# =====================================================
# INTENT CLASSIFIER PROMPT
# =====================================================

INTENT_PROMPT = """
Classify the user's message into ONE intent.

INTENTS:
- panic      (confusion, anxiety, "I'm overwhelmed", "stop")
- override   (wants change: "I have more time", "I hate this path")
- explain    (why did you choose this? what is my status?)
- roadmap    (what should I do next? show me the plan)
- learn      (technical doubts, coding questions, "how does React work?")
- casual     (hello, thanks, small talk)

Return STRICT JSON:
{ "intent": "<one_of_above>" }
"""


# =====================================================
# MAIN CHAT HANDLER
# =====================================================

def chat(user_state: UserState, user_message: str) -> Dict[str, Any]:
    """
    Main chat entry point. Routes based on intent.
    """

    # 1. Detect Intent
    try:
        intent_resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": INTENT_PROMPT},
                {"role": "user", "content": user_message}
            ],
            temperature=0.0,
            response_format={"type": "json_object"}
        )
        intent = json.loads(intent_resp.choices[0].message.content)["intent"]
    except Exception:
        intent = "casual"

    # 2. Route to Specialized Agents

    # A. Write Actions (Handled by Orchestrator logic)
    if intent in ["panic", "override"]:
        return orchestrator.handle_user_interaction(
            user_state=user_state,
            message=user_message,
            intent=intent
        )

    # B. Read Actions (Direct Agent calls)
    if intent == "explain":
        return explain_decision(user_state)

    if intent == "roadmap":
        # We regenerate the roadmap view (read-only)
        return generate_roadmap(user_state)

    # C. Learning Support (The Adaptive Tutor)
    if intent == "learn":
        return _safe_tutor(user_state, user_message)

    # D. Casual / Fallback
    return {
        "response_type": "casual",
        "message": "I'm FigureIt, your career strategist. You can ask me to **explain my decisions**, **show your roadmap**, or **help you learn** a concept."
    }


# =====================================================
# ADAPTIVE TUTOR MODE (The "God Level" Upgrade)
# =====================================================

def _safe_tutor(user_state: UserState, question: str) -> Dict[str, Any]:
    """
    Answers learning questions.
    ADAPTS teaching style based on Evidence Flags.
    """

    # 1. Analyze User Gaps
    flags = user_state.evidence_profile.flags
    focus = user_state.decision_state.focus[0] if user_state.decision_state.focus else "General Tech"

    # 2. Customize the Persona
    style_instruction = "Balance theory and code."

    if "theory_heavy" in flags:
        style_instruction = "User is Theory Heavy. Prioritize PRACTICAL CODE EXAMPLES. Show, don't just tell."
    elif "implementation_heavy" in flags:
        style_instruction = "User is Implementation Heavy. Prioritize UNDERLYING CONCEPTS (How it works under the hood)."
    elif "dsa_beginner" in flags:
        style_instruction = "User is a Beginner. Use analogies and simple language. No jargon."

    system_prompt = f"""
    You are a Senior Technical Mentor.

    CONTEXT:
    - User Focus: {focus}
    - Teaching Style: {style_instruction}

    RULES:
    - Teach clearly and concisely.
    - Do NOT suggest new career paths (stay in the {focus} lane).
    - If the user asks about a different path, remind them of their current focus.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ],
            temperature=0.3  # Precise but helpful
        )

        return {
            "response_type": "tutor",
            "answer": response.choices[0].message.content,
            "teaching_style_used": style_instruction  # For debugging/UI feedback
        }

    except Exception as e:
        return {"error": str(e)}