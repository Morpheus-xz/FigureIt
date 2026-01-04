"""
FigureIt — Evidence Profiler Demo (v3.0)

PURPOSE:
- Live test Evidence Profiler using real GitHub & LeetCode data
- Verify:
  1. Human-readable evidence tags
  2. ML-ready encoded feature vector

NOTE:
- This file is ONLY for development sanity checks
- Will NOT exist in production
"""

from ai_engine.models.user_state import UserState, BasicProfile
from ai_engine.agents.evidence_profiler import build_evidence
from ai_engine.data_pipeline.scrapers import (
    get_github_stats,
    get_leetcode_stats
)

# =====================================================
# DEMO CONFIG
# =====================================================

GITHUB_USERNAME = "Morpheus-xz"      # change if needed
LEETCODE_USERNAME = "Morpheus-xz"    # change if needed


# =====================================================
# RUN DEMO
# =====================================================

def run_demo():
    print("\n🔥 RUNNING FIGUREIT EVIDENCE PROFILER v3.0\n")

    # 1️⃣ Create Dummy UserState
    user = UserState(
        user_id="demo_user_001",
        basic_profile=BasicProfile(
            college_tier=3,
            year_of_study=2,
            time_availability=10
        )
    )

    # 2️⃣ Fetch Raw Data
    print("📥 Fetching GitHub data...")
    github_stats = get_github_stats(GITHUB_USERNAME)
    print(github_stats)

    print("\n📥 Fetching LeetCode data...")
    leetcode_stats = get_leetcode_stats(LEETCODE_USERNAME)
    print(leetcode_stats)

    # 3️⃣ Build Evidence Profile
    user = build_evidence(
        user_state=user,
        github_stats=github_stats,
        leetcode_stats=leetcode_stats
    )

    evidence = user.evidence_profile

    # 4️⃣ Display Results
    print("\n=== 🧠 EVIDENCE PROFILE (HUMAN VIEW) ===")
    for flag in evidence.flags:
        print(f" - {flag}")

    print("\n=== 🤖 ENCODED FEATURES (ML VIEW) ===")
    for feature, value in evidence.encoded_features.items():
        print(f"{feature}: {value}")

    print("\n=== 📊 RAW DATA SNAPSHOT ===")
    print("GitHub:", evidence.github_stats)
    print("LeetCode:", evidence.leetcode_stats)

    print("\n✅ Evidence Profiler Demo Complete\n")


# =====================================================
# ENTRY POINT
# =====================================================

if __name__ == "__main__":
    run_demo()
