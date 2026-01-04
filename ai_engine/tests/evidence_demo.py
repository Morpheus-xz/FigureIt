from ai_engine.models.user_state import UserState, BasicProfile
from ai_engine.data_pipeline.scrapers import (
    get_github_stats,
    get_leetcode_stats
)
from ai_engine.agents.evidence_profiler import build_evidence
print("🔥 RUNNING EVIDENCE PROFILER v2.1 FROM:", __file__)



def run_live_evidence_test():
    print("\n=== FIGUREIT: LIVE EVIDENCE PROFILER TEST ===\n")

    # 1️⃣ Create a dummy user (you)
    user = UserState(
        user_id="vedansh_live",
        basic_profile=BasicProfile(
            college_tier=3,
            year_of_study=2,
            time_availability=10
        )
    )

    # 2️⃣ Fetch REAL data
    github_username = "Morpheus-xz"
    leetcode_username = "Morpheus-xz"

    print("Fetching GitHub data...")
    github_stats = get_github_stats(github_username)
    print(github_stats)

    print("\nFetching LeetCode data...")
    leetcode_stats = get_leetcode_stats(leetcode_username)
    print(leetcode_stats)

    # 3️⃣ Run Evidence Profiler
    user = build_evidence(user, github_stats, leetcode_stats)

    # 4️⃣ Print results
    print("\n=== EVIDENCE PROFILE RESULT ===")
    print("Flags Detected:")
    for flag in user.evidence_profile.flags:
        print(f" - {flag}")

    print("\nRaw GitHub Stats:")
    print(user.evidence_profile.github_stats)

    print("\nRaw LeetCode Stats:")
    print(user.evidence_profile.leetcode_stats)


if __name__ == "__main__":
    run_live_evidence_test()

