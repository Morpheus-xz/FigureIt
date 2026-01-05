import json
import logging
from typing import Dict
from openai import OpenAI

from ai_engine.market.market_state import MarketState, SkillMarketSignal

logger = logging.getLogger(__name__)


class MarketPulse:
    """
    Converts market signals into bounded decision multipliers.

    - Deterministic logic for known skills (hard data)
    - LLM inference ONLY for unknown skills
    - Cached to minimize token usage
    - Outputs bounded multipliers safe for decision engines
    """

    # -----------------------------
    # Configuration
    # -----------------------------

    TREND_MULTIPLIERS = {
        "rising": 1.1,
        "stable": 1.0,
        "declining": 0.9,
        "niche": 0.9
    }

    SATURATION_PENALTIES = {
        "high": -0.15,
        "medium": 0.0,
        "low": 0.1
    }

    MIN_MULTIPLIER = 0.7
    MAX_MULTIPLIER = 1.3

    def __init__(self, client: OpenAI):
        """
        :param client: Initialized OpenAI client
        """
        self.client = client
        self.state = MarketState()
        self._cache: Dict[str, float] = {}

    # -----------------------------
    # Deterministic Logic
    # -----------------------------

    @staticmethod
    def _normalize_skill(skill: str) -> str:
        """Normalizes skill names for consistent lookup."""
        return skill.strip().lower()

    @staticmethod
    def _calculate_trend(current: int, previous: int) -> str:
        """Determines trend direction using ±15% threshold."""
        if previous == 0:
            return "rising"

        delta = (current - previous) / previous

        if delta >= 0.15:
            return "rising"
        if delta <= -0.15:
            return "declining"
        return "stable"

    def _known_skill_multiplier(self, signal: SkillMarketSignal) -> float:
        """Calculates multiplier using hard market data."""
        multiplier = 1.0

        # Demand signal
        if signal.jobs > 4500:
            multiplier += 0.2
        elif signal.jobs > 2500:
            multiplier += 0.1
        elif signal.jobs < 1000:
            multiplier -= 0.1

        # Trend signal
        trend = self._calculate_trend(signal.jobs, signal.previous_jobs)
        multiplier *= self.TREND_MULTIPLIERS.get(trend, 1.0)

        # Saturation penalty / bonus
        multiplier += self.SATURATION_PENALTIES.get(signal.saturation, 0.0)

        return round(
            min(max(multiplier, self.MIN_MULTIPLIER), self.MAX_MULTIPLIER),
            2
        )

    # -----------------------------
    # LLM Classification (Unknown Skills)
    # -----------------------------

    def _classify_unknown_skill(self, skill: str) -> float:
        """
        Uses LLM to classify unknown skill trend.
        Result is cached for future calls.
        """
        normalized = self._normalize_skill(skill)

        if normalized in self._cache:
            return self._cache[normalized]

        system_prompt = """
You are a hiring-market analyst.

Classify the hiring trend of the given skill relative to
mainstream software engineering roles.

Valid values ONLY:
- rising
- stable
- declining
- niche

Respond with strict JSON only.
"""

        user_prompt = f"""
Skill: "{skill}"

Return:
{{ "trend": "<value>" }}
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.0,
                response_format={"type": "json_object"}
            )

            data = json.loads(response.choices[0].message.content)
            trend = data.get("trend", "stable").lower()

            multiplier = self.TREND_MULTIPLIERS.get(trend, 1.0)

            self._cache[normalized] = multiplier
            return multiplier

        except Exception as e:
            logger.error(f"MarketPulse LLM failure for '{skill}': {e}")
            return 1.0

    # -----------------------------
    # Public API
    # -----------------------------

    def get_market_multiplier(self, skill: str) -> float:
        """
        Returns a decision-safe multiplier for ANY skill.
        """
        normalized = self._normalize_skill(skill)

        signal = self.state.skills.get(normalized)

        if signal:
            return self._known_skill_multiplier(signal)

        return self._classify_unknown_skill(skill)

    def snapshot(self) -> Dict:
        """
        Returns a serializable view of the current market state.
        """
        return {
            "generated_at": self.state.generated_at,  # already ISO string
            "skills": {
                skill_name: {
                    "jobs": data.jobs,
                    "trend": self._calculate_trend(data.jobs, data.previous_jobs),
                    "saturation": data.saturation,
                    "multiplier": self.get_market_multiplier(skill_name)
                }
                for skill_name, data in self.state.skills.items()
            }
        }

