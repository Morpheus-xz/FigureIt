# ai_engine/tests/orchestrator_demo.py

import json
from ai_engine.orchestrator import Orchestrator


def run_demo():
    print("🔥 RUNNING FIGUREIT ORCHESTRATOR DEMO\n")

    orchestrator = Orchestrator()

    result = orchestrator.run_full_analysis(
        user_id="demo_user_001",
        basic_data={
            "college_tier": 3,
            "year": 3,
            "hours": 5,
            "constraints": []
        },
        interest_answers={
            "q1": "I like building APIs and backend systems",
            "q2": "I don't enjoy frontend much"
        },
        github_username="torvalds",     # can be dummy
        leetcode_username="neal_wu"     # can be dummy
    )

    print("🧠 ORCHESTRATOR OUTPUT:\n")
    print(json.dumps(result, indent=2))
    print("\n✅ Orchestrator Demo Complete")

if __name__ == "__main__":
    run_demo()
