"""
Orchestrator — FigureIt (v1.0 STABLE)

ROLE:
- Central controller of the AI system
- Runs agents in the correct order
- Owns the lifecycle of UserState
- Single entry point for API & chatbot
"""

from typing import Dict, Any
import logging

# =========================
# MODELS
# =========================
from ai_engine.models.user_state import UserState, BasicProfile

# =========================
# CORE AGENTS (Logic First)
# =========================
from ai_engine.agents.context_profiler import build_context
from ai_engine.agents.evidence_profiler import build_evidence
from ai_engine.agents.decision_engine import make_decision

# =========================
# LLM AGENTS (Language Layer)
# =========================
from ai_engine.agents.interest_chatbot import analyze_interests
from ai_engine.agents.roadmap_generator import generate_roadmap
from ai_engine.agents.explanation_bot import explain_decision
from ai_engine.agents.panic_bot import handle_panic
from ai_engine.agents.override_interpreter import interpret_override

# =========================
# DATA PIPELINE
# =========================
from ai_engine.data_pipeline.scrapers import (
    get_github_stats,
    get_leetcode_stats
)

# =========================
# LOGGING
# =========================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FigureIt-Orchestrator")

from datetime import datetime

def _json_safe(obj):
    """
    Recursively converts datetime objects to ISO strings.
    """
    if isinstance(obj, dict):
        return {k: _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_json_safe(i) for i in obj]
    if isinstance(obj, datetime):
        return obj.isoformat()
    return obj

class Orchestrator:
    """
    Central Nervous System of FigureIt.
    """

    # -------------------------------------------------
    # MAIN PIPELINE
    # -------------------------------------------------
    def run_full_analysis(
        self,
        user_id: str,
        basic_data: Dict[str, Any],
        interest_answers: Dict[str, str],
        github_username: str,
        leetcode_username: str
    ) -> Dict[str, Any]:

        logger.info(f"🚀 Starting full analysis for {user_id}")

        # 1️⃣ Create UserState
        user_state = UserState(
            user_id=user_id,
            basic_profile=BasicProfile(
                college_tier=basic_data.get("college_tier", 3),
                year_of_study=basic_data.get("year", 1),
                time_availability=basic_data.get("hours", 10),
                constraints=basic_data.get("constraints", [])
            )
        )

        # 2️⃣ Context
        user_state = build_context(user_state)

        # 3️⃣ Evidence
        gh = get_github_stats(github_username)
        lc = get_leetcode_stats(leetcode_username)
        user_state = build_evidence(user_state, gh, lc)

        # 4️⃣ Interests (LLM)
        user_state = analyze_interests(user_state, interest_answers)

        # 5️⃣ Decision (Math)
        user_state = make_decision(user_state)

        # 6️⃣ Roadmap (LLM)
        roadmap = generate_roadmap(user_state)

        # 7️⃣ Explanation (LLM)
        explanation = explain_decision(user_state)

        raw_output = {
            "status": "success",
            "user_id": user_id,
            "profile": {
                "context": {
                    "urgency": user_state.context_profile.urgency_level.name,
                    "strictness": user_state.context_profile.strictness_level.name,
                    "max_focus": user_state.context_profile.max_focus_skills
                },
                "evidence_flags": user_state.evidence_profile.flags,
                "interest_bias": user_state.interest_profile.interest_bias
            },
            "decisions": {
                "focus": user_state.decision_state.focus,
                "park": user_state.decision_state.park,
                "drop": user_state.decision_state.drop
            },
            "roadmap": roadmap,
            "explanation": explanation
        }

        return _json_safe(raw_output)

    # -------------------------------------------------
    # INTERACTIVE MODES
    # -------------------------------------------------
    def handle_interaction(
        self,
        user_state: UserState,
        message: str,
        intent: str
    ) -> Dict[str, Any]:

        if intent == "panic":
            return handle_panic(user_state, message)

        if intent == "override":
            return {
                "action": "override_request",
                "changes": interpret_override(user_state, message)
            }

        return {"error": "Unknown intent"}
