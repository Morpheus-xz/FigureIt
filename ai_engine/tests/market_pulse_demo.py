"""
Market Pulse Demo — FigureIt

Purpose:
- Verify deterministic multipliers for known skills
- Verify LLM-based inference for unknown skills
- Verify caching behavior
- Verify JSON-safe snapshot
"""

import os
import json
from dotenv import load_dotenv
from openai import OpenAI

from ai_engine.market.market_pulse import MarketPulse

# -------------------------------------------------
# DEMO RUNNER
# -------------------------------------------------

def run_demo():
    print("🔥 RUNNING FIGUREIT MARKET PULSE DEMO\n")

    load_dotenv()

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    pulse = MarketPulse(client=client)

    # ---------------------------------------------
    # 1. Known Skills (Deterministic)
    # ---------------------------------------------
    known_skills = [
        "Python",
        "React",
        "AWS",
        "Rust"
    ]

    print("📊 KNOWN SKILL MULTIPLIERS (Deterministic):")
    for skill in known_skills:
        multiplier = pulse.get_market_multiplier(skill)
        print(f"  ✔ {skill:<10} → {multiplier}x")

    # ---------------------------------------------
    # 2. Unknown Skills (LLM Inference)
    # ---------------------------------------------
    unknown_skills = [
        "Blockchain",
        "iOS Development",
        "Android Development",
        "HTMX"
    ]

    print("\n🤖 UNKNOWN SKILL MULTIPLIERS (LLM-Inferred):")
    for skill in unknown_skills:
        multiplier = pulse.get_market_multiplier(skill)
        print(f"  ✔ {skill:<20} → {multiplier}x")

    # ---------------------------------------------
    # 3. Cache Verification
    # ---------------------------------------------
    print("\n🧠 CACHE VERIFICATION (No LLM Call Expected):")
    for skill in unknown_skills:
        multiplier = pulse.get_market_multiplier(skill)
        print(f"  ✔ {skill:<20} → {multiplier}x (cached)")

    # ---------------------------------------------
    # 4. Full Market Snapshot
    # ---------------------------------------------
    print("\n📸 MARKET SNAPSHOT (JSON-SAFE):")
    snapshot = pulse.snapshot()
    print(json.dumps(snapshot, indent=2))

    print("\n✅ Market Pulse Demo Complete")


# -------------------------------------------------
# ENTRY POINT
# -------------------------------------------------

if __name__ == "__main__":
    run_demo()
