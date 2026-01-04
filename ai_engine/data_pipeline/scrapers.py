import requests
from collections import Counter
from datetime import datetime

# ==========================================
# CONFIGURATION
# ==========================================
TIMEOUT_SECONDS = 5
GITHUB_API_BASE = "https://api.github.com"
LEETCODE_API_BASE = "https://alfa-leetcode-api.onrender.com"


# ==========================================
# TASK 3: THE CLEANER (Helper Function)
# ==========================================
def clean_language(language):
    """
    Normalizes messy language names.
    Example: 'Jupyter Notebook' -> 'Python'
    """
    if not language:
        return "None"

    lang_lower = language.lower()

    if "jupyter" in lang_lower:
        return "Python"
    if "html" in lang_lower or "css" in lang_lower:
        return "Web Basics"
    if "c++" in lang_lower:
        return "C++"

    return language


# ==========================================
# TASK 1: THE GITHUB FETCHER
# ==========================================
def get_github_stats(username):
    """
    Fetches comprehensive GitHub stats:
    - Repo Count, Stars, Forks (Impact)
    - Top Language (Cleaned)
    - Account Age (Experience)
    """
    if not username:
        return None

    headers = {"Accept": "application/vnd.github.v3+json"}

    try:
        # 1. Get User Profile (For Account Age)
        user_url = f"{GITHUB_API_BASE}/users/{username}"
        user_resp = requests.get(user_url, headers=headers, timeout=TIMEOUT_SECONDS)

        if user_resp.status_code == 404:
            print(f"[GitHub] User '{username}' not found.")
            return None

        user_data = user_resp.json()
        account_created = user_data.get("created_at", "")[:10]  # YYYY-MM-DD

        # 2. Get Repositories (For Stars, Forks, Languages)
        repos_url = f"{GITHUB_API_BASE}/users/{username}/repos?per_page=100"
        repos_resp = requests.get(repos_url, headers=headers, timeout=TIMEOUT_SECONDS)

        total_stars = 0
        total_forks = 0
        all_languages = []

        if repos_resp.status_code == 200:
            repos_data = repos_resp.json()
            for repo in repos_data:
                # Summing up metrics
                total_stars += repo.get("stargazers_count", 0)
                total_forks += repo.get("forks_count", 0)

                # Collecting Language
                lang = repo.get("language")
                if lang:
                    all_languages.append(clean_language(lang))  # <--- Applying The Cleaner

        # 3. Determine Top Language
        top_language = "None"
        if all_languages:
            top_language = Counter(all_languages).most_common(1)[0][0]

        return {
            "valid": True,
            "username": username,
            "repos": user_data.get("public_repos", 0),
            "stars": total_stars,
            "forks": total_forks,
            "top_lang": top_language,
            "account_created": account_created
        }

    except requests.exceptions.RequestException as e:
        print(f"[GitHub] Connection Error: {e}")
        return None


# ==========================================
# TASK 2: THE LEETCODE FETCHER
# ==========================================
def get_leetcode_stats(username):
    """
    Fetches CP stats using the Alfa API.
    """
    if not username:
        return None

    # Using the specific 'solved' endpoint as requested
    url = f"{LEETCODE_API_BASE}/{username}/solved"

    try:
        response = requests.get(url, timeout=TIMEOUT_SECONDS)

        if response.status_code != 200:
            return None

        data = response.json()

        # Validation
        if "solvedProblem" not in data:
            return None

        return {
            "valid": True,
            "username": username,
            "total_solved": data.get("solvedProblem", 0),
            "easy": data.get("easySolved", 0),
            "medium": data.get("mediumSolved", 0),
            "hard": data.get("hardSolved", 0),
            # Note: The 'solved' endpoint doesn't always provide acceptance rate.
            # We stick to the reliable solved counts for the MVP.
        }

    except requests.exceptions.RequestException as e:
        print(f"[LeetCode] Connection Error: {e}")
        return None


# ==========================================
# TEST BLOCK (Run this file to verify)
# ==========================================
if __name__ == "__main__":
    print("--- TESTING UPDATED GITHUB SCRAPER ---")
    # Test with a user who definitely has forks and older account
    print(get_github_stats("torvalds"))

    print("\n--- TESTING LEETCODE SCRAPER ---")
    print(get_leetcode_stats("neal_wu"))