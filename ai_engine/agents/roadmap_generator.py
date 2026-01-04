"""
Roadmap Generator — FigureIt (v2.1 PRODUCTION)

ROLE:
- Generates a personalized learning roadmap AFTER decisions are made
- Prunes skills the user already has (Evidence)
- Aligns projects with user interests
- Respects time constraints (Context)

IMPORTANT:
- This agent NEVER makes decisions
- It ONLY compiles a roadmap for the chosen focus
- Safe even if evidence is partially missing
"""

import os
import json
from typing import Dict, Any, List
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

from ai_engine.models.user_state import UserState

# =====================================================
# ENV SETUP
# =====================================================

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# =====================================================
# SYSTEM PROMPT (LLM AS CURRICULUM COMPILER)
# =====================================================

SYSTEM_PROMPT = """
You are a Senior Engineering Mentor designing a learning roadmap.

You DO NOT decide the career path.
The path is already chosen.

INPUTS YOU RECEIVE:
- Focus Path (career goal)
- Time per week
- Evidence Flags (what the user already has / lacks)
- Primary Interests

RULES:
- OUTPUT STRICT JSON ONLY
- No markdown
- No explanations
- No extra text

ROADMAP RULES:
- 4 phases only
- Each phase has:
  - phase_name
  - week_range
  - status: completed | active | locked
  - topics (specific, technical)
  - actionable_task (build something real)

- Skip basics if evidence suggests competence
- Projects must align with interests if provided
- If time_per_week < 8 → micro-tasks only

JSON SCHEMA:
{
  "roadmap_title": "string",
  "focus_path": "string",
  "project_theme": "string",
  "phases": [
    {
      "phase_name": "string",
      "week_range": "string",
      "status": "completed | active | locked",
      "topics": ["string"],
      "actionable_task": "string"
    }
  ]
}
"""

# =====================================================
# MAIN GENERATOR
# =====================================================

def generate_roadmap(user_state: UserState) -> Dict[str, Any]:
    """
    Generates a roadmap using FINAL user state.
    JSON-safe, deterministic, production-ready.
    """

    # -------------------------
    # 1. SAFETY CHECKS
    # -------------------------

    if not user_state.decision_state:
        return {"error": "Decision state missing. Run decision engine first."}

    if not user_state.decision_state.focus:
        return {"error": "No focus path selected."}

    focus_path = user_state.decision_state.focus[0]
    hours = user_state.basic_profile.time_availability

    # -------------------------
    # 2. SAFE EXTRACTION
    # -------------------------

    evidence_flags: List[str] = []
    github_top_language = None

    if user_state.evidence_profile:
        evidence_flags = user_state.evidence_profile.flags
        github_top_language = user_state.evidence_profile.github_stats.get("top_lang")

    interest_bias = (
        user_state.interest_profile.interest_bias
        if user_state.interest_profile
        else {}
    )
    primary_interests = [k for k, v in interest_bias.items() if v >= 0.5]

    # -------------------------
    # 3. BUILD LLM PAYLOAD
    # -------------------------

    payload = {
        "focus_path": focus_path,
        "hours_per_week": hours,
        "github_top_language": github_top_language,
        "evidence_flags": evidence_flags,
        "primary_interests": primary_interests
    }

    # -------------------------
    # 4. LLM CALL
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

        # Manual JSON safety (guards against extra text)
        start = raw.find("{")
        end = raw.rfind("}") + 1
        roadmap = json.loads(raw[start:end])

        # ✅ JSON-safe metadata
        roadmap["generated_at"] = datetime.now().isoformat()

        return roadmap

    except Exception as e:
        print(f"❌ Roadmap generation failed: {e}")
        return _fallback_roadmap(focus_path)

# =====================================================
# FALLBACK (NO LLM / FAILURE SAFE)
# =====================================================

def _fallback_roadmap(focus_path: str) -> Dict[str, Any]:
    """
    Guaranteed safe fallback roadmap.
    """
    return {
        "roadmap_title": f"{focus_path} Starter Roadmap",
        "focus_path": focus_path,
        "project_theme": "Generic Portfolio Project",
        "generated_at": datetime.now().isoformat(),
        "phases": [
            {
                "phase_name": "Foundations",
                "week_range": "Weeks 1–2",
                "status": "active",
                "topics": ["Core Language", "Basic Tooling"],
                "actionable_task": "Build a simple CLI or script."
            },
            {
                "phase_name": "Core Development",
                "week_range": "Weeks 3–4",
                "status": "locked",
                "topics": ["Framework Basics", "Project Structure"],
                "actionable_task": "Build a basic CRUD app."
            },
            {
                "phase_name": "Applied Build",
                "week_range": "Weeks 5–6",
                "status": "locked",
                "topics": ["Real-world Scenarios"],
                "actionable_task": "Extend project with a real use-case."
            },
            {
                "phase_name": "Polish & Deploy",
                "week_range": "Weeks 7–8",
                "status": "locked",
                "topics": ["Testing", "Deployment"],
                "actionable_task": "Deploy project publicly."
            }
        ]
    }
