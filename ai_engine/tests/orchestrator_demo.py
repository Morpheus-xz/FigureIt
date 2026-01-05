"""
Orchestrator Demo — FigureIt (FINAL)

Validates:
- Full pipeline
- Market-aware decisions
- Advisor + Roadmap + Explanation
"""

from ai_engine.orchestrator import Orchestrator
import json


def run_demo():
    print("🔥 RUNNING FIGUREIT ORCHESTRATOR DEMO\n")

    orchestrator = Orchestrator()

    result = orchestrator.run_full_analysis(
        user_id="demo_user_001",
        basic_data={
            "college_tier": 3,
            "year": 3,
            "hours": 6,
            "constraints": []
        },
        interest_answers={
            "q1": "I love building applications",
            "q2": "I enjoy problem solving but not heavy math"
        },
        github_username="torvalds",      # replace if needed
        leetcode_username="neal_wu"      # replace if needed
    )

    print("🧠 ORCHESTRATOR OUTPUT:\n")
    print(json.dumps(result, indent=2))
    print("\n✅ Orchestrator Demo Complete\n")


if __name__ == "__main__":
    run_demo()
