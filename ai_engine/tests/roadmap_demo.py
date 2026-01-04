"""
Roadmap Generator Demo — FigureIt
Shows how the roadmap will appear in the website tab.
"""

import json
from ai_engine.agents.roadmap_generator import generate_roadmap
from ai_engine.models.user_state import (
    UserState,
    BasicProfile,
    EvidenceProfile,
    InterestProfile,
    DecisionState,
    Confidence
)

def run_demo():
    print("\n🔥 RUNNING FIGUREIT ROADMAP GENERATOR DEMO\n")

    # -------------------------
    # MOCK USER (POST-DECISION)
    # -------------------------

    user = UserState(
        user_id="demo_user",
        basic_profile=BasicProfile(
            college_tier=3,
            year_of_study=3,
            time_availability=6
        )
    )

    user.decision_state = DecisionState(
        focus=["Backend Engineering"]
    )

    user.evidence_profile = EvidenceProfile(
        github_stats={
            "top_lang": "Python",
            "valid": True
        },
        flags=[
            "projects_show_real_world_signal",
            "portfolio_needs_polish"
        ]
    )

    user.interest_profile = InterestProfile(
        interest_bias={
            "development": 0.8,
            "data": 0.6
        },
        confidence_level=Confidence.HIGH,
        exploration_allowed=False
    )

    # -------------------------
    # GENERATE ROADMAP
    # -------------------------

    roadmap = generate_roadmap(user)

    # -------------------------
    # DISPLAY (WEBSITE STYLE)
    # -------------------------

    print(f"🎯 ROADMAP TITLE: {roadmap.get('roadmap_title')}")
    print(f"🧭 FOCUS PATH: {roadmap.get('focus_path')}")
    print(f"💡 PROJECT THEME: {roadmap.get('project_theme')}\n")

    for phase in roadmap.get("phases", []):
        print(f"🔹 {phase['phase_name']} ({phase['week_range']})")
        print(f"   Status: {phase['status']}")
        print(f"   Topics:")
        for t in phase["topics"]:
            print(f"     - {t}")
        print(f"   Build Task: {phase['actionable_task']}\n")

    print("✅ Roadmap Demo Complete\n")


if __name__ == "__main__":
    run_demo()
